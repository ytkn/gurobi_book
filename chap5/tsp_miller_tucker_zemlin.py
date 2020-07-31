import sys
import os
import itertools
import pulp
import networkx
from graph_utils import *
from typing import List, Dict, Union, Tuple

sys.path.append('../')

from common import logger, solve_with_log


def make_problem_by_loose_constraint(G: networkx.DiGraph, n: int) -> pulp.LpProblem:
    log = logger.get_logger(__name__)
    problem = pulp.LpProblem(name="tsp", sense=pulp.LpMinimize)

    x = {(i, j): pulp.LpVariable(name='x_{}_{}'.format(i, j), cat=pulp.LpBinary)
         for (i, j) in G.edges}

    u = {i: pulp.LpVariable(name='u_{}'.format(i), cat=pulp.LpInteger)
         for i in range(n)}

    problem.objective += sum(
        [x[i, j] * G[i][j]['weight'] for (i, j) in G.edges])

    problem.addConstraint(u[0] >= 0)
    problem.addConstraint(u[0] <= 0)

    for i in range(1, n):
        problem.addConstraint(u[i] >= 1)
        problem.addConstraint(u[i] <= n - 1)

    for i, j in itertools.product(range(n), range(1, n)):
        if i != j:
            problem.addConstraint(u[i] + 1 - (n - 1) * (1 - x[i, j]) <= u[j])

    for i in range(n):
        except_i = list(range(n))
        except_i.remove(i)
        problem.addConstraint(sum([x[i, j] for j in except_i]) >= 1)
        problem.addConstraint(sum([x[i, j] for j in except_i]) <= 1)
        problem.addConstraint(sum([x[j, i] for j in except_i]) >= 1)
        problem.addConstraint(sum([x[j, i] for j in except_i]) <= 1)

    return problem


def make_problem_by_tight_constraint(G: networkx.DiGraph, n: int) -> pulp.LpProblem:
    log = logger.get_logger(__name__)
    problem = pulp.LpProblem(name="tsp", sense=pulp.LpMinimize)

    x = {(i, j): pulp.LpVariable(name='x_{}_{}'.format(i, j), cat=pulp.LpBinary)
         for (i, j) in G.edges}

    u = {i: pulp.LpVariable(name='u_{}'.format(i), cat=pulp.LpInteger)
         for i in range(n)}

    problem.objective += pulp.lpSum(
        [x[i, j] * G[i][j]['weight'] for (i, j) in G.edges])

    problem.addConstraint(u[0] >= 0)
    problem.addConstraint(u[0] <= 0)

    for i in range(1, n):
        problem.addConstraint(u[i] - (n - 3) * x[i, 0] + x[0, i] >= 2)
        problem.addConstraint(u[i] - x[i, 0] + (n - 3) * x[0, i] <= n - 2)

    for i, j in itertools.product(range(n), range(1, n)):
        if i != j:
            problem.addConstraint(
                u[i] + 1 - (n - 1) * (1 - x[i, j]) + (n - 3) * x[j, i] <= u[j])

    for i in range(n):
        except_i = list(range(n))
        except_i.remove(i)
        problem.addConstraint(pulp.lpSum([x[i, j] for j in except_i]) >= 1)
        problem.addConstraint(pulp.lpSum([x[i, j] for j in except_i]) <= 1)
        problem.addConstraint(pulp.lpSum([x[j, i] for j in except_i]) >= 1)
        problem.addConstraint(pulp.lpSum([x[j, i] for j in except_i]) <= 1)

    return problem


def solve(problem: pulp.LpProblem, G: networkx.DiGraph) -> List[Edge]:
    solve_with_log.exec(problem, time_limit=60)
    variables_dict = problem.variablesDict()
    solution = []
    for (i, j) in G.edges:
        if variables_dict[f"x_{i}_{j}"].varValue == 1:
            solution.append((i, j))
    return solution


def main():
    logger.set_logger()
    log = logger.get_logger(__name__)
    n = 40
    x, y = make_points(n)
    graph = to_directed_graph(make_euclidean_graph(n, x, y))
    problem_loose = make_problem_by_loose_constraint(graph, n)
    problem_tight = make_problem_by_tight_constraint(graph, n)
    solution = solve(problem_loose, graph)
    plot_graph(solution, x, y)
    solution = solve(problem_tight, graph)
    plot_graph(solution, x, y)


if __name__ == "__main__":
    main()
