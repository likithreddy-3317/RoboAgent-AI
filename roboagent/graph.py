from langgraph.graph import StateGraph, START, END
from .state import RoboState
from .agents import order_agent, inventory_agent, planning_agent, allocation_agent, route_agent, execution_agent, monitoring_agent, replanning_agent, report_agent

def build_graph():
    g = StateGraph(RoboState)
    nodes = {
        "order_agent": order_agent, "inventory_agent": inventory_agent,
        "planning_agent": planning_agent, "allocation_agent": allocation_agent,
        "route_agent": route_agent, "execution_agent": execution_agent,
        "monitoring_agent": monitoring_agent, "replanning_agent": replanning_agent,
        "report_agent": report_agent,
    }
    for name, fn in nodes.items(): g.add_node(name, fn)
    g.add_edge(START, "order_agent")
    for a, b in [("order_agent","inventory_agent"),("inventory_agent","planning_agent"),
                 ("planning_agent","allocation_agent"),("allocation_agent","route_agent"),
                 ("route_agent","execution_agent"),("execution_agent","monitoring_agent")]:
        g.add_edge(a, b)
    def next_step(state):
        return "replanning_agent" if any(t["status"] != "completed" for t in state.get("tasks", [])) else "report_agent"
    g.add_conditional_edges("monitoring_agent", next_step, {"replanning_agent":"replanning_agent", "report_agent":"report_agent"})
    g.add_edge("replanning_agent", "report_agent")
    g.add_edge("report_agent", END)
    return g.compile()
