from roboagent.warehouse import fresh_inventory, inventory_lookup, shortest_path

def test_inventory_lookup():
    assert inventory_lookup("keyboard", fresh_inventory())["found"]
    assert not inventory_lookup("unknown", fresh_inventory())["found"]

def test_shortest_path():
    path, cost = shortest_path("START", "PACKING")
    assert path[0] == "START" and path[-1] == "PACKING" and cost > 0
