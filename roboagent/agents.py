import os
import re
from langchain_ollama import ChatOllama
from .models import WarehouseOrder
from .state import RoboState
from .warehouse import fresh_inventory, fresh_robots, inventory_lookup, shortest_path

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")


def order_agent(state: RoboState):
    llm = ChatOllama(model=MODEL, temperature=0)
    parser = llm.with_structured_output(WarehouseOrder)

    raw_order = state["raw_order"]
    prompt = f"""
Extract the warehouse order accurately.

Supported products: wireless mouse, keyboard, usb-c hub, camera, tripod.

Rules:
- Extract ONLY products explicitly requested by the user.
- Preserve every requested quantity exactly.
- Extract the order ID if the user provides one.
- Use ORDER-1001 only when no order ID is provided.
- Set priority to high when the user says high-priority.
- Use PACKING as the delivery station.

User request: {raw_order}
"""
    order = parser.invoke(prompt)
    order_data = order.model_dump()

    # Preserve an explicitly provided numeric order ID.
    match = re.search(
        r"\border\s+(\d+)\b",
        raw_order,
        re.IGNORECASE,
    )
    if match:
        order_data["order_id"] = match.group(1)

    state["order"] = order_data
    return state


def inventory_agent(state: RoboState):
    inventory = fresh_inventory()
    checks = []
    for item in state["order"]["items"]:
        check = inventory_lookup(item["product"], inventory)
        check["requested"] = item["quantity"]
        check["in_stock"] = check["found"] and check["available"] >= item["quantity"]
        checks.append(check)
    state["inventory_check"] = {"all_available": all(x["in_stock"] for x in checks), "items": checks}
    return state

def planning_agent(state: RoboState):
    tasks = []
    for i, item in enumerate(state["order"]["items"], 1):
        key = item["product"].strip().lower()
        check = next((x for x in state["inventory_check"]["items"] if x["product"] == key), None)
        if check and check["in_stock"]:
            tasks.append({"task_id": f"T{i}", "product": key, "quantity": item["quantity"], "location": check["location"], "status": "planned"})
    state["tasks"] = tasks
    if not state["inventory_check"]["all_available"]:
        state["issues"] = state.get("issues", []) + ["One or more requested products are unavailable or insufficient."]
    return state

def allocation_agent(state: RoboState):
    robots = fresh_robots()
    usable = sorted([(rid, x) for rid, x in robots.items() if x["battery"] >= 30], key=lambda z: -z[1]["battery"])
    assignments = []
    for i, task in enumerate(state["tasks"]):
        if not usable:
            state["issues"] = state.get("issues", []) + [f"No safe robot available for {task['task_id']}."]
            break
        rid, robot = usable[i % len(usable)]
        assignments.append({"task_id": task["task_id"], "robot_id": rid})
        robot["status"] = "assigned"
    state["robot_assignments"], state["robot_status"] = assignments, robots
    return state

def route_agent(state: RoboState):
    by_id = {t["task_id"]: t for t in state["tasks"]}
    routes = []
    for a in state["robot_assignments"]:
        t = by_id[a["task_id"]]
        p1, c1 = shortest_path("START", t["location"])
        p2, c2 = shortest_path(t["location"], "PACKING")
        routes.append({**a, "product": t["product"], "path_to_pick": p1, "path_to_packing": p2, "estimated_cost": c1+c2})
    state["routes"] = routes
    return state

def execution_agent(state: RoboState):
    log = state.get("execution_log", [])
    inject = os.getenv("ROBOAGENT_INJECT_FAILURE", "0") == "1"
    failed = False
    task_map = {t["task_id"]: t for t in state["tasks"]}
    for route in state["routes"]:
        rid = route["robot_id"]
        if inject and not failed and rid == "R1":
            state["robot_status"][rid]["status"] = "failed"
            log.append(f"ALERT: simulated {rid} failure during {route['task_id']}.")
            state["issues"] = state.get("issues", []) + [f"Simulated failure: {rid} stopped."]
            failed = True
            continue
        log += [f'{rid}: travel {" -> ".join(route["path_to_pick"])}.',
                f'{rid}: pick {route["product"]} x{task_map[route["task_id"]]["quantity"]}.',
                f'{rid}: deliver via {" -> ".join(route["path_to_packing"])}.',
                f'{rid}: complete {route["task_id"]}.']
        task_map[route["task_id"]]["status"] = "completed"
        state["robot_status"][rid]["status"] = "available"
        state["robot_status"][rid]["location"] = "PACKING"
        state["robot_status"][rid]["battery"] = max(0, state["robot_status"][rid]["battery"] - route["estimated_cost"]*2)
    state["execution_log"], state["replanned"] = log, failed
    return state

def monitoring_agent(state: RoboState):
    incomplete = [t for t in state["tasks"] if t["status"] != "completed"]
    if incomplete:
        state["issues"] = state.get("issues", []) + [f"{len(incomplete)} task(s) incomplete after execution."]
    return state


def replanning_agent(state: RoboState):
    robots = state["robot_status"]
    tasks = state["tasks"]
    log = state.get("execution_log", [])
    assignments = state.get("robot_assignments", [])

    for task in tasks:
        if task["status"] == "completed":
            continue

        # Select a functioning robot with sufficient battery.
        alternatives = [
            (rid, robot)
            for rid, robot in robots.items()
            if robot["status"] != "failed"
            and robot["battery"] >= 30
        ]
        alternatives.sort(
            key=lambda pair: pair[1]["battery"],
            reverse=True,
        )

        if not alternatives:
            log.append(
                f"REPLAN BLOCKED: no safe robot for {task['task_id']}."
            )
            state.setdefault("issues", []).append(
                f"Recovery failed for {task['task_id']}: "
                "no safe robot available."
            )
            continue

        rid, robot = alternatives[0]

        # Recalculate the route for the incomplete task.
        p1, c1 = shortest_path("START", task["location"])
        p2, c2 = shortest_path(task["location"], "PACKING")
        cost = c1 + c2

        # Verify that the robot can complete the route safely.
        if robot["battery"] - cost * 2 < 0:
            log.append(
                f"REPLAN BLOCKED: insufficient battery for {rid}."
            )
            state.setdefault("issues", []).append(
                f"Recovery failed for {task['task_id']}: "
                f"insufficient battery on {rid}."
            )
            continue

        # Simulate the recovery execution, not just the plan.
        log.append(
            f"REPLAN: assign {task['task_id']} to {rid}."
        )
        log.append(
            f"{rid}: travel {' -> '.join(p1)}."
        )
        log.append(
            f"{rid}: pick {task['product']} x{task['quantity']}."
        )
        log.append(
            f"{rid}: deliver via {' -> '.join(p2)}."
        )
        log.append(
            f"{rid}: complete {task['task_id']} after replanning."
        )

        # Update task, assignment, and robot state consistently.
        task["status"] = "completed"
        assignments = [
            a for a in assignments
            if a["task_id"] != task["task_id"]
        ]
        assignments.append({
            "task_id": task["task_id"],
            "robot_id": rid,
        })

        robot["location"] = "PACKING"
        robot["status"] = "available"
        robot["battery"] -= cost * 2

    state["execution_log"] = log
    state["robot_status"] = robots
    state["robot_assignments"] = assignments
    state["replanned"] = True
    return state


def report_agent(state: RoboState):
    state["final_report"] = {
        "project": "RoboAgent AI", "order": state.get("order", {}),
        "inventory_available": state.get("inventory_check", {}).get("all_available", False),
        "inventory_checks": state.get("inventory_check", {}).get("items", []),
        "tasks": state.get("tasks", []), "robot_assignments": state.get("robot_assignments", []),
        "routes": state.get("routes", []), "execution_log": state.get("execution_log", []),
        "robot_status_final": state.get("robot_status", {}), "issues": state.get("issues", []),
        "replanned": state.get("replanned", False),
        "completed_tasks": sum(t["status"] == "completed" for t in state.get("tasks", [])),
        "total_tasks": len(state.get("tasks", []))
    }
    return state
