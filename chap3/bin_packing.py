import sys
import os
import itertools
import pulp
from typing import List, Dict, Union

sys.path.append('../')

from common import logger, solve_with_log

instance_dir = os.path.join("instances", "bin_packing")


def bins_by_greedy(bin_capacity: int, items: List[int]) -> int:
    bins = [[]]
    for item in sorted(items, reverse=True):
        find = False
        for bin in bins:
            if sum(bin) + item <= bin_capacity:
                bin.append(item)
                find = True
                break
        if not find:
            bins.append([item])
        bins.sort(key=lambda x: sum(x), reverse=True)
    return len(bins)


def make_solution_by_greedy(bin_capacity: int, items: List[int]) -> List[List[int]]:
    bins = [[]]
    used = [False for _ in range(len(items))]
    for item in sorted(items, reverse=True):
        find = False
        for bin in bins:
            if sum(bin) + item <= bin_capacity:
                bin.append(item)
                find = True
                break
        if not find:
            bins.append([item])
        bins.sort(key=lambda x: sum(x), reverse=True)
    solution = []
    for bin in bins:
        l = [0 for _ in range(len(items))]
        for packed in bin:
            for i in range(len(items)):
                if (not used[i]) and (items[i] == packed):
                    l[i] = 1
                    used[i] = True
                    break
        solution.append(l)
    return solution


def make_simple_solution(bin_capacity: int, items: List[int]) -> List[List[int]]:
    solution = []
    for i in range(len(items)):
        l = [0 for _ in items]
        l[i] = 1
        solution.append(l)
    return solution


def make_problem(bin_capacity: int, items: List[int]) -> pulp.LpProblem:
    log = logger.get_logger(__name__)
    n_bins = bins_by_greedy(bin_capacity, items)
    log.debug(f"greedy:{n_bins}")
    n_items = len(items)
    problem = pulp.LpProblem(name="bin_packing", sense=pulp.LpMinimize)
    x = {(i, j): pulp.LpVariable(name='x_{}_{}'.format(i, j), cat=pulp.LpBinary)
         for i, j in itertools.product(range(n_bins), range(n_items))}

    t = {i: pulp.LpVariable(name='t_{}'.format(i), cat=pulp.LpBinary)
         for i in range(n_bins)}

    for i in range(n_bins):
        problem.addConstraint(pulp.lpSum(
            [x[i, j] * items[j] for j in range(n_items)]) <= bin_capacity, name=f"capcacity_{i}")

    for j in range(n_items):
        problem.addConstraint(pulp.lpSum(
            [x[i, j] for i in range(n_bins)]) >= 1)
        problem.addConstraint(pulp.lpSum(
            [x[i, j] for i in range(n_bins)]) <= 1)

    for i, j in itertools.product(range(n_bins), range(n_items)):
        problem.addConstraint(t[i] >= x[i, j])

    problem.objective += pulp.lpSum([t[i] for i in range(n_bins)])
    return problem


# initial solution should be given by list of binnary with size of n_bins x n_items
def make_problem_with_initial_solution(bin_capacity: int, items: List[int], initial_solution: List[List[int]]) -> pulp.LpProblem:
    log = logger.get_logger(__name__)
    n_bins = len(initial_solution)
    log.debug(f"greedy:{n_bins}")
    n_items = len(items)
    problem = pulp.LpProblem(name="bin_packing", sense=pulp.LpMinimize)
    x = {(i, j): pulp.LpVariable(name='x_{}_{}'.format(i, j), cat=pulp.LpBinary)
         for i, j in itertools.product(range(n_bins), range(n_items))}

    for i, j in itertools.product(range(n_bins), range(n_items)):
        x[i, j].setInitialValue(initial_solution[i][j])

    t = {i: pulp.LpVariable(name='t_{}'.format(i), cat=pulp.LpBinary)
         for i in range(n_bins)}

    for i in range(n_bins):
        t[i].setInitialValue(1)

    for i in range(n_bins):
        problem.addConstraint(pulp.lpSum(
            [x[i, j] * items[j] for j in range(n_items)]) <= bin_capacity, name=f"capcacity_{i}")

    for j in range(n_items):
        problem.addConstraint(pulp.lpSum(
            [x[i, j] for i in range(n_bins)]) >= 1)
        problem.addConstraint(pulp.lpSum(
            [x[i, j] for i in range(n_bins)]) <= 1)

    for i, j in itertools.product(range(n_bins), range(n_items)):
        problem.addConstraint(t[i] >= x[i, j])

    problem.objective += pulp.lpSum([t[i] for i in range(n_bins)])
    return problem


def read_from_text(idx: int) -> Union[int, List[int]]:
    path = os.path.join(instance_dir, "binpack1.txt")
    with open(path) as f:
        n_instances = int(f.readline().replace("\n", ""))
        instances = []
        for _ in range(n_instances):
            f.readline()
            l = f.readline().replace("\n", "").split(' ')
            bin_capacity = int(l[0])
            n_items = int(l[1])
            items = [int(f.readline().replace("\n", ""))
                     for _ in range(n_items)]
            instances.append([bin_capacity, items])
    f.close()
    return instances[idx]


def make_instance() -> Union[int, List[int]]:
    bin_capacity = 9
    w = [2, 3, 4, 5, 6, 7, 8]
    q = [5, 2, 6, 6, 2, 2, 2]
    items = list(itertools.chain.from_iterable(
        [[sz for _ in range(cnt)] for sz, cnt in zip(w, q)]))
    return bin_capacity, items


def main():
    logger.set_logger()
    log = logger.get_logger(__name__)

    bin_capacity, items = read_from_text(0)
    # bin_capacity, items = make_instance()
    # initial_solution = make_solution_by_greedy(bin_capacity, items)
    initial_solution = make_simple_solution(bin_capacity, items)
    solutions_str = "\n".join([f"{row}" for row in initial_solution])
    log.debug(f"=========initial_solution=========\n{solutions_str}")
    problem = make_problem_with_initial_solution(
        bin_capacity, items, initial_solution)
    # problem = make_problem(bin_capacity, items)
    solve_with_log.exec(problem, True, 300)


if __name__ == "__main__":
    main()
    l = [1]
