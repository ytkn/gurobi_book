import sys
import os
import itertools
import pulp
import random
from typing import List, Dict, Union, Tuple

sys.path.append('../')

from common import logger, solve_with_log

Edge = Tuple[int, int]


def count_stanfing_bit(n: int, s: int) -> int:
    return sum([1 if s & (1 << i) else 0 for i in range(n)])


def count_different(s: int, edges: List[Edge]):
    return len(list(
        filter(lambda x: ((s & (1 << x[0])) == 0) != ((s & (1 << x[1])) == 0), edges)))


def solution_by_enumeration(n: int, edges: List[Edge]) -> int:
    return min([count_different(s, edges) if count_stanfing_bit(n, s) * 2 == n else n**2
                for s in range(1 << n)])


# n should be even
def make_problem(n: int, edges: List[Edge]) -> pulp.LpProblem:
    log = logger.get_logger(__name__)
    problem = pulp.LpProblem(name="bin_packing", sense=pulp.LpMinimize)
    x = {i: pulp.LpVariable(name='x_{}'.format(
        i), cat=pulp.LpBinary) for i in range(n)}
    y = {(i, j): pulp.LpVariable(name='y_{}_{}'.format(
        i, j), cat=pulp.LpBinary) for i, j in edges}

    problem.objective += pulp.lpSum([y[i, j] for i, j in edges])

    problem.addConstraint(pulp.lpSum([x[i] for i in range(n)]) >= n / 2)
    problem.addConstraint(pulp.lpSum([x[i] for i in range(n)]) <= n / 2)
    for i, j in edges:
        problem.addConstraint(x[i] - x[j] <= y[i, j])
        problem.addConstraint(x[j] - x[i] <= y[i, j])
    return problem


def make_edges(n: int, p: float) -> List[Edge]:
    edges = []
    for i, j in itertools.combinations(range(n), 2):
        if random.random() < p:
            edges.append((i, j))
    return edges


def main():
    logger.set_logger()
    log = logger.get_logger(__name__)
    n = 10
    p = 0.4
    edges = make_edges(n, p)
    problem = make_problem(n, edges)
    solve_with_log.exec(problem, False, 100)
    log.debug(f"by enumeration: {solution_by_enumeration(n, edges)}")
    log.debug(F"edges:{edges}")


if __name__ == "__main__":
    main()
