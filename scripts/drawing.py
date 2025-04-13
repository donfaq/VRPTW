# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "matplotlib",
#     "networkx",
# ]
# ///

import argparse
from itertools import cycle
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import colors


def parse_point(line):
    """Parse a line of customer data into a dict"""
    fields = ["number", "x", "y", "demand", "ready_time", "due_date", "service_time"]
    values = line.strip().split()
    return {k: int(v) for k, v in zip(fields, values)}


def parse_solution(solution_str):
    """Parse solution string into list of routes"""
    return solution_str.strip().split("\n")


def create_graph(points, routes):
    """Create NetworkX graph from points and routes"""
    G = nx.Graph()
    G.add_nodes_from(range(len(points)))

    for route in routes:
        route_nodes = list(map(int, route.split()[::2]))
        G.add_path(route_nodes)
    return G


def get_paths(routes):
    """Extract edge paths from routes"""
    paths = []
    for route in routes:
        path = []
        route_nodes = list(map(int, route.split()[::2]))
        for i in range(len(route_nodes) - 1):
            path.append((route_nodes[i], route_nodes[i + 1]))
        paths.append(path)
    return paths


def draw_solution(points, paths, output_file):
    """Draw the solution using matplotlib"""
    G = nx.Graph()
    pos = {p["number"]: (p["x"], p["y"]) for p in points}

    fig, ax = plt.subplots(figsize=(15, 15), dpi=300)

    color_cycle = cycle(colors.TABLEAU_COLORS)
    for path in paths:
        path_color = next(color_cycle)
        nodes_in_path = {x for p in path for x in p}
        node_sizes = [p["demand"] for p in points if p["number"] in nodes_in_path]

        nx.draw_networkx_edges(G, pos=pos, edgelist=path, ax=ax, edge_color=path_color)
        nx.draw_networkx_nodes(
            G,
            pos=pos,
            nodelist=nodes_in_path,
            node_size=node_sizes,
            node_color=path_color,
            ax=ax,
        )

    plt.savefig(output_file, dpi=300)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Draw solution")
    parser.add_argument(
        "instance",
        type=str,
        help="Path to the problem file (in Solomon format)",
    )
    parser.add_argument(
        "solution", type=str, help="Path to the solution file"
    )
    parser.add_argument(
        "--out", type=str, help="Path to the output file", default="output.png"
    )
    return parser.parse_args()


def main() -> None:
    args = arguments()

    instance_path = Path(args.instance)
    output_path = Path(args.out)
    solution_path = Path(args.solution)

    # Read and parse input data
    with open(instance_path, "r") as f:
        data = f.readlines()
    points = list(map(parse_point, data[9:]))

    # Parse solution and create graph
    with open(solution_path, "r") as f:
        solution = f.read()

    routes = parse_solution(solution)
    paths = get_paths(routes)

    # Draw and save solution
    draw_solution(points, paths, output_path)


if __name__ == "__main__":
    main()
