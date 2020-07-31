import sys
import os
import itertools
import pulp
from typing import List, Dict, Union, Tuple

sys.path.append('../')

from common import logger, solve_with_log

instance_dir = os.path.join("instances", "graph_coloring")

Edge = Tuple[int, int]


def read_instance(file: str) -> Union[int, List[Edge]]:
    path = os.path.join(instance_dir, file)
    with open(path) as f:
        l = f.readline().replace("\n", "").split(' ')
        n = int(l[2])
        n_edges = int(l[3])
        edges = []
        for _ in range(n_edges):
            l = f.readline().replace("\n", "").split(' ')
            if int(l[1]) < int(l[2]):
                edges.append((int(l[1]) - 1, int(l[2]) - 1))
    f.close()
    return n, edges


def make_problem_for_feasibility(n: int, edges: List[Edge], n_colors: int) -> pulp.LpProblem:
    log = logger.get_logger(__name__)
    problem = pulp.LpProblem(name="graph_coloring", sense=pulp.LpMinimize)
    x = {(i, j): pulp.LpVariable(name=f"x_{i}_{j}", cat=pulp.LpBinary)
         for i, j in itertools.product(range(n), range(n_colors))}
    z = {(i, j): pulp.LpVariable(name=f"z_{i}_{j}", cat=pulp.LpBinary)
         for i, j in edges}

    problem.objective += pulp.lpSum([z[i, j] for i, j in edges])

    problem.addConstraint(pulp.lpSum([z[i, j] for i, j in edges]) <= 0)

    for i in range(n):
        problem.addConstraint(pulp.lpSum(
            [x[i, j] for j in range(n_colors)]) >= 1)
        problem.addConstraint(pulp.lpSum(
            [x[i, j] for j in range(n_colors)]) <= 1)

    for (i, j), k in itertools.product(edges, range(n_colors)):
        problem.addConstraint(x[i, k] + x[j, k] <= 1 + z[i, j])
    return problem


def binary_seach(n: int, edges: List[Edge]) -> int:
    log = logger.get_logger(__name__)
    lb = 1
    rb = n
    while rb - lb > 1:
        c = int((lb + rb) / 2)
        problem = make_problem_for_feasibility(n, edges, c)
        problem.solve(pulp.PULP_CBC_CMD(msg=False))
        log.debug(f"c:{c}, status:{pulp.LpStatus[problem.status]}")
        if pulp.LpStatus[problem.status] == "Infeasible":
            lb = c
        else:
            rb = c
    return rb


def main():
    logger.set_logger()
    log = logger.get_logger(__name__)
    n, edges = read_instance("queen5_5.col")
    opt = binary_seach(n, edges)
    log.debug(f"opt:{opt}")


if __name__ == "__main__":
    main()
