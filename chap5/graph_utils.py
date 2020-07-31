import random
import networkx
import itertools
import os
import math
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


def make_evil_points(n: int):
    x_base = [random.random() * 10 for _ in range((n + 9) // 10)]
    y_base = [random.random() * 10 for _ in range((n + 9) // 10)]
    x = [x_base[i // 10] + random.random() for i in range(n)]
    y = [y_base[i // 10] + random.random() for i in range(n)]
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
    plt.clf()


def to_directed_graph(g: networkx.Graph) -> networkx.Graph:
    G = networkx.DiGraph()
    for (i, j) in g.edges:
        G.add_edge(i, j, weight=g[i][j]['weight'])
        G.add_edge(j, i, weight=g[i][j]['weight'])
    return G


def deg2rad(x):
    return math.pi * x / 180.0


def read_hokkaido():
    r = 0.65 * 10000
    path = os.path.join('instances', 'hokkaido.txt')
    f = open(path, 'r')
    line = f.readline()
    lat = []
    longt = []
    while line:
        row = line.split(' ')
        lat.append(float(row[1]))
        longt.append(float(row[2].replace('\n', '')))
        line = f.readline()
    f.close()

    ave_lat = sum(lat) / len(lat)
    ave_longt = sum(longt) / len(longt)
    r_longt = r * math.cos(math.pi * ave_lat / 180)

    x = [deg2rad(l - ave_longt) * r_longt for l in longt]
    y = [deg2rad(l - ave_lat) * r for l in lat]
    n = len(x)
    return n, x, y
