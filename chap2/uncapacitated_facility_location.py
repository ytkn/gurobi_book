import sys
import os
import itertools
import pulp
from typing import List, Dict

sys.path.append('../')

from common import logger, solve_with_log

instance_dir = os.path.join("instances", "uflp")


class Instance:
    def __init__(self, n_facilities: int, n_customers: int, demands: List[int], transportation_cost: List[List[int]], establishment_cost: List[int]):
        self.n_facilities = n_facilities
        self.n_customers = n_customers
        self.demands = demands
        self.transportation_cost = transportation_cost
        self.establishment_cost = establishment_cost


def read_instance(path: str) -> Instance:
    with open(path) as f:
        l = f.readline().replace("\n", "").split(' ')
        n_facilities = int(l[0])
        n_customers = int(l[1])
        establishment_cost = []
        for _ in range(n_facilities):
            l = f.readline().replace("\n", "").split(' ')
            establishment_cost.append(float(l[1]))
        demands = []
        transportation_cost = []

        for _ in range(n_customers):
            d = int(f.readline().replace("\n", ""))
            demands.append(d)
            transportation_cost.append(
                [float(x) / d for x in f.readline().replace(" \n", "").split(' ')])

    f.close()
    return Instance(n_facilities, n_customers, demands, transportation_cost, establishment_cost)


def make_problem(instance: Instance):
    problem = pulp.LpProblem(name="facility_location", sense=pulp.LpMinimize)
    x = {(i, j): pulp.LpVariable(name='x_{}_{}'.format(i, j), cat=pulp.LpInteger)
         for i, j in itertools.product(range(instance.n_customers), range(instance.n_facilities))}
    y = {j: pulp.LpVariable(name='y_{}'.format(j), cat=pulp.LpBinary)
         for j in range(instance.n_facilities)}
    problem.objective += sum([instance.establishment_cost[j] * y[j]
                              for j in range(instance.n_facilities)])
    problem.objective += sum([instance.transportation_cost[i][j] * x[i, j]
                              for i, j in itertools.product(range(instance.n_customers), range(instance.n_facilities))])

    for i, j in itertools.product(range(instance.n_customers), range(instance.n_facilities)):
        problem.addConstraint(x[i, j] >= 0, name=f"x_positive_{i}_{j}")

    for i in range(instance.n_customers):
        problem.addConstraint(sum([x[i, j] for j in range(instance.n_facilities)]) >= instance.demands[i],
                              name=f"customer_demands_positive_{i}")
        problem.addConstraint(sum([x[i, j] for j in range(instance.n_facilities)]) <= instance.demands[i],
                              name=f"customer_demands_negative_{i}")

    sum_demands = sum([d for d in instance.demands])
    for j in range(instance.n_facilities):
        problem.addConstraint(sum([x[i, j] for i in range(instance.n_customers)]) <= y[j] * sum_demands,
                              name=f"capacity_{j}")
    return problem


def main():
    instance = read_instance(os.path.join(instance_dir, "cap71.txt"))
    problem = make_problem(instance)
    solve_with_log.exec(problem, False, 300)


if __name__ == "__main__":
    logger.set_logger()
    main()
