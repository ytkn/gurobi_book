import sys
import os
import itertools
import pulp
import networkx
from graph_utils import *
from typing import List, Dict, Union, Tuple

sys.path.append('../')

from common import logger, solve_with_log


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
        log.info(f"components: {len(components)}")
        for c in components:
            log.info(c)
        if len(components) == 1:
            solved = True
        else:
            for component in components:
                problem.addConstraint(sum([x[min(i, j), max(i, j)] for i, j in itertools.combinations(component, 2)])
                                      <= len(component) - 1)

    solution = []
    log.info("solved")
    for (i, j) in G.edges:
        if pulp.value(x[i, j]) == 1:
            solution.append((i, j))

    return solution


def main():
    logger.set_logger()
    log = logger.get_logger(__name__)
    n = 50
    x, y = make_points(n)
    graph = make_euclidean_graph(n, x, y)
    solution = make_problem_and_solve(graph, n)
    plot_graph(solution, x, y)


if __name__ == "__main__":
    main()
