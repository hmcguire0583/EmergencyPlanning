import heapq

def build_graph(locations, roads):
    graph = {loc['id']: [] for loc in locations}
    for road in roads:
        graph[road['from_id']].append((road['to_id'], road['travel_time_minutes']))
    return graph

def dijkstra(graph, start):
    queue = [(0, start, [start])]
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
    depot_id = 0
    trucks = [f"Truck {i+1}" for i in range(data["meta"]["trucks"])]
    truck_capacity = data["meta"]["truck_capacity"]

    supply_locs = [loc for loc in locations if loc["demand"] > 0]
    demand_map = {loc["id"]: loc["demand"] for loc in supply_locs}
    supplies_delivered = {loc["name"]: 0 for loc in supply_locs}
    truck_usage = {t: 0 for t in trucks}
    truck_routes = {t: [] for t in trucks}
    truck_idx = 0

    while any(demand_map.values()):
        truck = trucks[truck_idx % len(trucks)]
        truck_load = 0
        curr = depot_id
        route = [depot_id]
        total_time = 0
        visited_this_run = set()

        while truck_load < truck_capacity and any(demand_map.values()):
            dists, paths = dijkstra(graph, curr)
            candidates = [
                (dists[l], l) for l in demand_map
                if demand_map[l] > 0 and l in dists and l not in visited_this_run
                and demand_map[l] <= (truck_capacity - truck_load)
            ]
            if not candidates:
                break
            dist, chosen = min(candidates)
            deliverable = demand_map[chosen]
            truck_load += deliverable
            demand_map[chosen] = 0
            loc_name = next(loc["name"] for loc in supply_locs if loc["id"] == chosen)
            supplies_delivered[loc_name] += deliverable
            route += paths[chosen][1:]  # Skip current node
            total_time += dist
            curr = chosen
            visited_this_run.add(chosen)

        # Return to depot
        if curr != depot_id:
            dists_back, paths_back = dijkstra(graph, curr)
            route += paths_back[depot_id][1:]
            total_time += dists_back[depot_id]

        truck_usage[truck] += 1
        truck_routes[truck].append((route, total_time))
        truck_idx += 1

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