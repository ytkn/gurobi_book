import sys
import os
import itertools
import pulp
from typing import List, Dict, Union, Tuple

sys.path.append('../')

from common import logger, solve_with_log


class Instance:
    def __init__(self, n_products: int, n_terms: int, setup_cost: List[List[int]], setup_time: List[List[int]],
                 production_cost: List[List[int]], stock_cost: List[List[int]], demand: List[List[int]], time_limit: List[int]):
        self.n_products = n_products
        self.n_terms = n_terms
        self.setup_cost = setup_cost
        self.setup_time = setup_time
        self.production_cost = production_cost
        self.stock_cost = stock_cost
        self.demand = demand
        self.time_limit = time_limit


def make_variables(instance: Instance):
    n_products = instance.n_products
    n_terms = instance.n_terms

    stock = {(p, t): pulp.LpVariable(name='stock_{}_{}'.format(p, t), cat=pulp.LpInteger)
             for p, t in itertools.product(range(n_products), range(n_terms))}

    production = {(p, t): pulp.LpVariable(name='production_{}_{}'.format(p, t), cat=pulp.LpInteger)
                  for p, t in itertools.product(range(n_products), range(n_terms))}

    setup = {(p, t): pulp.LpVariable(name='setup_{}_{}'.format(p, t), cat=pulp.LpBinary)
             for p, t in itertools.product(range(n_products), range(n_terms))}

    return stock, production, setup


def make_problem(instance: Instance, stock: pulp.LpVariable, production: pulp.LpVariable, setup: pulp.LpVariable):
    log = logger.get_logger(__name__)
    log.debug(instance.time_limit)
    n_products = instance.n_products
    n_terms = instance.n_terms

    problem = pulp.LpProblem(name="lot_sizing", sense=pulp.LpMinimize)

    problem.objective += pulp.lpSum([
        instance.setup_cost[p][t] * setup[p, t] +
        instance.production_cost[p][t] * production[p, t] +
        instance.stock_cost[p][t] * stock[p, t]
        for p, t in itertools.product(range(n_products), range(n_terms))
    ])

    for p in range(n_products):
        problem.addConstraint(stock[p, 0] >= 0)
        problem.addConstraint(stock[p, 0] <= 0)

    for p, t in itertools.product(range(n_products), range(n_terms)):
        problem.addConstraint(production[p, t] >= 0)

    for p, t in itertools.product(range(n_products), range(1, n_terms)):
        problem.addConstraint(stock[p, t] >= 0)

    for p, t in itertools.product(range(n_products), range(1, n_terms)):
        problem.addConstraint(
            stock[p, t] >= stock[p, t - 1] + production[p, t - 1] - instance.demand[p][t - 1])
        problem.addConstraint(
            stock[p, t] <= stock[p, t - 1] + production[p, t - 1] - instance.demand[p][t - 1])

    for p in range(n_products):
        problem.addConstraint(
            stock[p, n_terms - 1] + production[p, n_terms - 1] - instance.demand[p][n_terms - 1] >= 0)

    for t in range(n_terms):
        problem.addConstraint(
            pulp.lpSum([instance.setup_time[p][t] * setup[p, t] + production[p, t]
                        for p in range(n_products)]) <= instance.time_limit[t])

    for p, t in itertools.product(range(n_products), range(n_terms)):
        problem.addConstraint(production[p, t] <=
                              setup[p, t] * (instance.time_limit[t] - instance.setup_time[p][t]))

    return problem


def make_simple_instance():
    n_terms = 5
    setup_time = [[0 for _ in range(n_terms)]]
    setup_cost = [[3 for _ in range(n_terms)]]
    production_cost = [[1, 1, 3, 3, 3]]
    stock_cost = [[1 for _ in range(n_terms)]]
    demand = [[5, 7, 3, 6, 4]]
    sum_demand = sum(demand[0])
    time_limit = [sum_demand for _ in range(n_terms)]

    return Instance(1, n_terms, setup_cost, setup_time, production_cost, stock_cost, demand, time_limit)


def main():
    logger.set_logger()
    log = logger.get_logger(__name__)
    instance = make_simple_instance()
    stock, production, setup = make_variables(instance)
    problem = make_problem(instance, stock, production, setup)
    solve_with_log.exec(problem)
    for i in range(5):
        log.debug(
            f"{pulp.value(production[0, i])},{pulp.value(stock[0, i])},{pulp.value(setup[0, i])}")


if __name__ == "__main__":
    main()
