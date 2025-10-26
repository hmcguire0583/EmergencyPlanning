import heapq
import matplotlib.pyplot as plt
import networkx as nx

def build_graph(locations, roads):
    graph = {loc['id']: [] for loc in locations}
    for road in roads:
        if road.get("blocked", False):
            continue
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


def greedy_delivery(graph, depot_id, demand_map, truck_capacity, supply_locs):
    """
    Plan one truck run until it fills or no more demand can be served.
    Returns: (delivery_sequence, total_time, load, delivered_dict)
    """
    delivery_sequence = [depot_id]   # only depot + demand nodes
    total_time = 0
    truck_load = 0
    curr = depot_id
    delivered = {}

    while truck_load < truck_capacity and any(demand_map.values()):
        dists, _ = dijkstra(graph, curr)

        # choose closest valid demand location
        candidates = [
            (dists[l], l) for l in demand_map
            if demand_map[l] > 0 and l in dists
        ]
        if not candidates:
            break

        dist, chosen = min(candidates)

        # amount to deliver at this stop
        deliverable = min(demand_map[chosen], truck_capacity - truck_load)
        truck_load += deliverable
        demand_map[chosen] -= deliverable

        loc_name = next(loc["name"] for loc in supply_locs if loc["id"] == chosen)
        delivered[loc_name] = delivered.get(loc_name, 0) + deliverable

        total_time += dist
        curr = chosen
        delivery_sequence.append(chosen)

    # return to depot
    if curr != depot_id:
        dists_back, _ = dijkstra(graph, curr)
        total_time += dists_back[depot_id]
    delivery_sequence.append(depot_id)

    return delivery_sequence, total_time, truck_load, delivered


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
    truck_routes = {t: [] for t in trucks}
    truck_idx = 0

    while any(demand_map.values()):
        truck = trucks[truck_idx % len(trucks)]
        route, time, load, delivered = greedy_delivery(
            graph, depot_id, demand_map, truck_capacity, supply_locs
        )

        # merge delivered amounts into global supplies_delivered
        for loc, amt in delivered.items():
            supplies_delivered[loc] += amt

        truck_routes[truck].append((route, time, load))
        truck_idx += 1

    # pretty text output
    route_text = []
    for truck, routes in truck_routes.items():
        for idx, (route, time, load) in enumerate(routes):
            route_locs = [next(loc["name"] for loc in locations if loc["id"] == i) for i in route]
            route_text.append(
                f"{truck} - Run {idx+1}: {' -> '.join(route_locs)} | Time: {time} | Load: {load}"
            )

    route_text.append("\nSupplies Delivered:")
    route_text += [f"{loc}: {amt}" for loc, amt in supplies_delivered.items()]
    return "\n".join(route_text), truck_routes


def visualize_routes(data, truck_routes):
    """Draws the depot, shelters, and truck delivery routes."""
    G = nx.DiGraph()

    # Add nodes with coordinates
    pos = {}
    for loc in data["locations"]:
        pos[loc["id"]] = (loc["longitude"], loc["latitude"])
        G.add_node(loc["id"], label=loc["name"])

    # Add road edges
    for road in data["roads"]:
        if road.get("blocked", False):
            continue
        G.add_edge(road["from_id"], road["to_id"], weight=road["travel_time_minutes"])

    # Plot base graph (all roads in light gray)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=False, node_size=100, edge_color="lightgray")

    # Draw node labels
    labels = {loc["id"]: loc["name"] for loc in data["locations"]}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)

    # Color each truck’s route differently
    colors = ["red", "blue", "green", "orange", "purple", "brown"]
    for i, (truck, routes) in enumerate(truck_routes.items()):
        color = colors[i % len(colors)]
        for route, _, _ in routes:
            edges = list(zip(route[:-1], route[1:]))
            nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=color, width=2, arrows=True, alpha=0.8)

    # Highlight depot
    depot_id = 0
    nx.draw_networkx_nodes(G, pos, nodelist=[depot_id], node_color="yellow", node_size=500, label="Depot")

    plt.title("Truck Delivery Routes")
    plt.axis("equal")
    plt.show()
