from copy import deepcopy
import heapq

INITIAL_INVENTORY = {
    "wireless mouse": {"sku": "WM-01", "quantity": 12, "location": "A1"},
    "keyboard": {"sku": "KB-02", "quantity": 8, "location": "B2"},
    "usb-c hub": {"sku": "UH-03", "quantity": 6, "location": "C1"},
    "camera": {"sku": "CM-04", "quantity": 5, "location": "D2"},
    "tripod": {"sku": "TR-05", "quantity": 10, "location": "D1"},
}
INITIAL_ROBOTS = {
    "R1": {"location": "START", "battery": 92, "status": "available"},
    "R2": {"location": "START", "battery": 68, "status": "available"},
    "R3": {"location": "START", "battery": 24, "status": "available"},
}
GRAPH = {
    "START": {"A1": 2, "B2": 3, "C1": 4, "D1": 5, "D2": 6, "PACKING": 4},
    "A1": {"START": 2, "B2": 2, "PACKING": 3},
    "B2": {"START": 3, "A1": 2, "C1": 2, "PACKING": 2},
    "C1": {"START": 4, "B2": 2, "D1": 2, "PACKING": 3},
    "D1": {"START": 5, "C1": 2, "D2": 2, "PACKING": 3},
    "D2": {"START": 6, "D1": 2, "PACKING": 4},
    "PACKING": {"START": 4, "A1": 3, "B2": 2, "C1": 3, "D1": 3, "D2": 4},
}
def fresh_inventory(): return deepcopy(INITIAL_INVENTORY)
def fresh_robots(): return deepcopy(INITIAL_ROBOTS)
def inventory_lookup(product, inventory):
    key = product.strip().lower()
    if key not in inventory:
        return {"found": False, "product": key, "available": 0, "location": None}
    x = inventory[key]
    return {"found": True, "product": key, "available": x["quantity"], "location": x["location"], "sku": x["sku"]}
def shortest_path(start, goal):
    queue = [(0, start, [start])]
    best = {}
    while queue:
        cost, node, path = heapq.heappop(queue)
        if node == goal: return path, cost
        if node in best and best[node] <= cost: continue
        best[node] = cost
        for nxt, edge in GRAPH.get(node, {}).items():
            if cost + edge < best.get(nxt, float("inf")):
                heapq.heappush(queue, (cost + edge, nxt, path + [nxt]))
    raise ValueError(f"No route from {start} to {goal}")
