import sys
import os
import itertools
import pulp
from typing import List, Dict, Union, Tuple

sys.path.append('../')

from common import logger, solve_with_log


def make_problem(func, a: List[int]):
    log = logger.get_logger(__name__)
    n = len(a)
    b = [func(s) for s in a]
    z = {i: pulp.LpVariable(name=f"z_{i}", cat=pulp.LpContinuous)
         for i in range(n)}
    x = pulp.LpVariable(name="x", cat=pulp.LpContinuous)
    problem = pulp.LpProblem(name="convex_combination", sense=pulp.LpMinimize)
    problem.addConstraint(pulp.lpSum([z[i] * a[i] for i in range(n)]) >= x)
    problem.addConstraint(pulp.lpSum([z[i] * a[i] for i in range(n)]) <= x)
    problem.addConstraint(pulp.lpSum(z) <= 1)
    problem.addConstraint(pulp.lpSum(z) >= 1)
    for i in range(n):
        problem.addConstraint(z[i] >= 0)

    problem.objective += pulp.lpSum([z[i] * b[i] for i in range(n)])
    problem.sos2 = [z[i] for i in range(n)]
    solve_with_log.exec(problem)
    for i in range(n):
        log.info(pulp.value(z[i]))
    return problem


def target_func(x):
    return (x - 3)**2 + 5


def main():
    logger.set_logger()
    log = logger.get_logger(__name__)
    a = range(-5, 6)
    problem = make_problem(target_func, a)


if __name__ == "__main__":
    main()
