import heapq

def build_graph(locations, roads):
    graph = {loc['id']: [] for loc in locations}
    for road in roads:
        graph[road['from_id']].append((road['to_id'], road['travel_time_minutes']))
    return graph

def dijkstra(graph, start):
    queue = [(0, start, [])]
    visited = set()
    min_dists = {start: 0}
    paths = {start: [start]}
    while queue:
        dist, node, path = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        for neighbor, time in graph.get(node, []):
            new_cost = dist + time
            if neighbor not in min_dists or new_cost < min_dists[neighbor]:
                min_dists[neighbor] = new_cost
                paths[neighbor] = path + [neighbor]
                heapq.heappush(queue, (new_cost, neighbor, path + [neighbor]))
    return min_dists, paths

def compute_routes(data):
    locations = data["locations"]
    roads = data["roads"]
    graph = build_graph(locations, roads)
    depot_id = 0  # Depot is always id=0 in your file
    trucks = ["Truck 1", "Truck 2", "Truck 3"]
    truck_capacity = data["meta"]["truck_capacity"]

    supply_locs = [loc for loc in locations if loc["demand"] > 0]
    supply_queue = []
    for loc in supply_locs:
        supply_queue += [loc["id"]] * loc["demand"]

    result = []
    supplies_delivered = {loc["name"]: 0 for loc in supply_locs}
    truck_usage = {t: 0 for t in trucks}
    truck_routes = {t: [] for t in trucks}
    truck_idx = 0

    while supply_queue:
        truck = trucks[truck_idx % len(trucks)]
        truck_load = 0
        curr = depot_id
        route = [depot_id]
        total_time = 0
        while supply_queue and truck_load < truck_capacity:
            # Find closest supply location still needing goods
            dists, paths = dijkstra(graph, curr)
            candidates = [(dists[l], l) for l in set(supply_queue) if l in dists]
            if not candidates:
                break
            dist, chosen = min(candidates)
            truck_load += 1
            loc_name = next(loc["name"] for loc in supply_locs if loc["id"] == chosen)
            supplies_delivered[loc_name] += 1
            route += paths[chosen][1:]  # Skip current node
            total_time += dist
            curr = chosen
            supply_queue.remove(chosen)
        truck_usage[truck] += 1
        truck_routes[truck].append((route, total_time))

    # Output formatting
    route_text = []
    for truck, routes in truck_routes.items():
        for idx, (route, time) in enumerate(routes):
            route_locs = [next(loc["name"] for loc in locations if loc["id"] == i) for i in route]
            route_text.append(f"{truck} - Run {idx+1}: {' -> '.join(route_locs)} | Time: {time}")
    route_text.append("\nSupplies Delivered:")
    route_text += [f"{loc}: {amt}" for loc, amt in supplies_delivered.items()]
    route_text.append("\nTruck Usage:")
    route_text += [f"{truck}: {uses} runs" for truck, uses in truck_usage.items()]
    return "\n".join(route_text)
