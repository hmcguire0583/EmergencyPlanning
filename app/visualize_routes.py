import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

TRUCK_COLORS = ["orange", "green", "purple", "blue", "magenta"]

def build_graph(locations, roads):
    G = nx.Graph()
    for loc in locations:
        G.add_node(
            loc["id"],
            pos=(loc["longitude"], loc["latitude"]),
            name=loc["name"],
            demand=loc["demand"]
        )
    for road in roads:
        G.add_edge(
            road["from_id"],
            road["to_id"],
            weight=road["travel_time_minutes"]
        )
    return G

def animate_routes_popup(data, truck_routes):
    locations = data["locations"]
    roads = data["roads"]
    G = build_graph(locations, roads)
    pos = nx.get_node_attributes(G, 'pos')
    labels = nx.get_node_attributes(G, 'name')

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title(data["meta"]["name"], fontsize=14, fontweight='bold')

    # draw network
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.5, ax=ax)
    depot_id = 0
    node_colors = ['red' if n == depot_id else 'skyblue' for n in G.nodes]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=400, edgecolors='black', ax=ax)
    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold', ax=ax)

    # trucks
    truck_points = []
    for i, route in enumerate(truck_routes):
        point, = ax.plot([], [], 'o',
                         color=TRUCK_COLORS[i % len(TRUCK_COLORS)],
                         markersize=12, label=f"Truck {i+1}")
        truck_points.append((point, route))

    def update(frame):
        for point, route in truck_points:
            if frame < len(route):
                node_id = route[frame]
                x, y = pos[node_id]
                point.set_data([x], [y])   # FIX: wrap in list
        return [p[0] for p in truck_points]

    max_len = max(len(route) for route in truck_routes)
    FuncAnimation(fig, update, frames=max_len, interval=1000, blit=True, repeat=False)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_aspect('equal')
    ax.legend()
    plt.tight_layout()
    plt.show()   # <-- this makes the popup
