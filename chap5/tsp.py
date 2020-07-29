import sys
import os
import itertools
import pulp
import random
import networkx
from typing import List, Dict, Union, Tuple

sys.path.append('../')

from common import logger, solve_with_log


# not metric
def make_complete_graph(n: int) -> networkx.Graph:
    G = networkx.Graph()
    for i, j in itertools.combinations(range(n), 2):
        w = random.randint(1, 10)
        G.add_edge(i, j, weight=w)
    return G


def make_problem_and_solve(G: networkx.Graph, n: int):
    log = logger.get_logger(__name__)
    problem = pulp.LpProblem(name="tsp", sense=pulp.LpMinimize)

    x = {(i, j): pulp.LpVariable(name='x_{}_{}'.format(i, j), cat=pulp.LpBinary)
         for (i, j) in G.edges}

    problem.objective += sum(
        [x[i, j] * G[i][j]['weight'] for (i, j) in G.edges])

    for i in range(n):
        problem.addConstraint(
            sum([x[j, i] for j in range(0, i)]) +
            sum([x[i, j] for j in range(i + 1, n)])
            >= 2)
        problem.addConstraint(
            sum([x[j, i] for j in range(0, i)]) +
            sum([x[i, j] for j in range(i + 1, n)])
            <= 2)

    solved = False
    while not solved:
        problem.solve(pulp.PULP_CBC_CMD(msg=False))
        g = networkx.Graph()
        for (i, j) in G.edges:
            if pulp.value(x[i, j]) == 1:
                g.add_edge(i, j)
        components = list(networkx.connected_components(g))
        log.info(len(components))
        for c in components:
            log.info(c)
        if len(components) == 1:
            solved = True
        else:
            for component in components:
                problem.addConstraint(sum([x[min(i, j), max(i, j)] for i, j in itertools.combinations(component, 2)])
                                      <= len(component) - 1)

    log.info("solution")
    for (i, j) in G.edges:
        if pulp.value(x[i, j]) == 1:
            log.info(f"{i}, {j}")


def main():
    logger.set_logger()
    log = logger.get_logger(__name__)
    n = 20
    graph = make_complete_graph(n)
    make_problem_and_solve(graph, n)


if __name__ == "__main__":
    main()
