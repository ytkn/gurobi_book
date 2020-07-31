import sys
import os
import itertools
import pulp
from typing import List, Dict, Union, Tuple

sys.path.append('../')

from common import logger, solve_with_log

instance_dir = os.path.join("instances", "graph_coloring")


def make_instance() -> Union[List[int], List[int], List[int]]:
    processing_times = [1, 4, 2, 3, 1, 4]
    release_times = [4, 0, 2, 4, 1, 5]
    weights = [3, 1, 2, 3, 1, 2]
    return processing_times, release_times, weights


def make_problem_by_disjunctive_formulation(processing_times: List[int], release_times: List[int], weights: List[int]) -> pulp.LpProblem:
    log = logger.get_logger(__name__)
    problem = pulp.LpProblem(name="scheduling", sense=pulp.LpMinimize)
    n = len(weights)
    s = {i: pulp.LpVariable(name='s_{}'.format(i), cat=pulp.LpInteger)
         for i in range(n)}
    x = {(i, j): pulp.LpVariable(name='x_{}_{}'.format(i, j), cat=pulp.LpBinary)
         for i, j in itertools.product(range(n), range(n))}

    problem.objective += pulp.lpSum([weights[i] * (s[i] + processing_times[i])
                                     for i in range(n)])

    for i, j in itertools.combinations(range(n), 2):
        problem.addConstraint(x[i, j] + x[j, i] >= 1)
        problem.addConstraint(x[i, j] + x[j, i] <= 1)

    for i in range(n):
        problem.addConstraint(s[i] >= release_times[i])
    # Big M
    M = max(release_times) + pulp.lpSum(processing_times)

    for i, j in itertools.product(range(n), range(n)):
        problem.addConstraint(
            s[i] + processing_times[i] <= s[j] + M * (1 - x[i, j]))
    return problem


def make_problem_by_time_index(processing_times: List[int], release_times: List[int], weights: List[int]) -> pulp.LpProblem:
    log = logger.get_logger(__name__)
    problem = pulp.LpProblem(name="scheduling", sense=pulp.LpMinimize)
    n = len(weights)
    max_finish_time = max(release_times) + pulp.lpSum(processing_times)

    x = {(i, t): pulp.LpVariable(name='x_{}_{}'.format(i, j), cat=pulp.LpBinary)
         for i, t in itertools.product(range(n), range(max_finish_time))}

    problem.objective += pulp.lpSum([weights[i] * x[i, t] * (t + processing_times[i])
                                     for i, t in itertools.product(range(n), range(max_finish_time))])

    for i in range(n):
        problem.addConstraint(
            pulp.lpSum([x[i, t] for t in range(release_times[i], max_finish_time)]) >= 1)
        problem.addConstraint(
            pulp.lpSum([x[i, t] for t in range(release_times[i], max_finish_time)]) <= 1)

    # TODO constraint for forbid duplication
    # for t in range(max_finish_time):

    return problem


def main():
    logger.set_logger()
    log = logger.get_logger(__name__)
    processing_times, release_times, weights = make_instance()
    problem = make_problem_by_disjunctive_formulation(
        processing_times, release_times, weights)
    solve_with_log.exec(problem)
    variables_dict = problem.variablesDict()
    for k, v in variables_dict.items():
        log.info(f"{k}: {v.varValue}")


if __name__ == "__main__":
    main()
