import random
import networkx
import itertools
import os
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List, Dict, Union, Tuple

Edge = Tuple[int, int]


def dist(x1: float, x2: float, y1: float, y2: float) -> float:
    return (x2 - x1)**2 + (y2 - y1)**2


def make_points(n: int):
    x = [random.random() * 10 for _ in range(n)]
    y = [random.random() * 10 for _ in range(n)]
    return x, y


def make_euclidean_graph(n: int, x: List[float], y: List[float]) -> networkx.Graph:
    G = networkx.Graph()
    for i, j in itertools.combinations(range(n), 2):
        w = random.randint(1, 10)
        G.add_edge(i, j, weight=dist(x[i], x[j], y[i], y[j]))
    return G


# not metric
def make_complete_graph(n: int) -> networkx.Graph:
    G = networkx.Graph()
    for i, j in itertools.combinations(range(n), 2):
        w = random.randint(1, 10)
        G.add_edge(i, j, weight=w)
    return G


def edges_to_adjacent_list(edges: List[Edge], n: int) -> List[List[int]]:
    adjacent_list = [[] for _ in range(n)]
    for i, j in edges:
        adjacent_list[i].append(j)
        adjacent_list[j].append(i)
    return adjacent_list


def plot_graph(edges, x, y):
    n = len(x)
    adjacent_list = edges_to_adjacent_list(edges, n)
    for v in range(n):
        for to in adjacent_list[v]:
            if v < to:
                plt.plot([x[v], x[to]], [y[v], y[to]],
                         marker='o', c='red', linestyle="solid")

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(os.path.join("images", f"tsp_solution_{current_time}"))
