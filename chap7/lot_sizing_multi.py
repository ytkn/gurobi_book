import sys
import os
import itertools
import pulp
from typing import List, Dict, Union, Tuple

sys.path.append('../')

from common import logger, solve_with_log

instance_dir = 'instances'


class Instance:
    def __init__(self, n_products: int, n_terms: int, setup_cost: List[List[int]], stock_cost: int, demand: List[List[int]]):
        self.n_products = n_products
        self.n_terms = n_terms
        self.setup_cost = setup_cost
        self.stock_cost = stock_cost
        self.demand = demand


def make_variables(instance: Instance):
    n_products = instance.n_products
    n_terms = instance.n_terms

    stock = {(p, t): pulp.LpVariable(name='stock_{}_{}'.format(p, t), cat=pulp.LpInteger)
             for p, t in itertools.product(range(n_products), range(n_terms))}

    production = {(p, t): pulp.LpVariable(name='production_{}_{}'.format(p, t), cat=pulp.LpBinary)
                  for p, t in itertools.product(range(n_products), range(n_terms))}

    last_production = {(p, t): pulp.LpVariable(name='last_production_{}_{}'.format(p, t), cat=pulp.LpBinary)
                       for p, t in itertools.product(range(n_products), range(n_terms))}

    setup = {(p, q, t): pulp.LpVariable(name='setup_{}_{}_{}'.format(p, q, t), cat=pulp.LpBinary)
             for p, q, t in itertools.product(range(n_products), range(n_products), range(n_terms))}

    return stock, production, last_production, setup


def make_problem(instance: Instance, stock: pulp.LpVariable, production: pulp.LpVariable, last_production: pulp.LpVariable, setup: pulp.LpVariable):
    log = logger.get_logger(__name__)
    n_products = instance.n_products
    n_terms = instance.n_terms

    problem = pulp.LpProblem(name="lot_sizing", sense=pulp.LpMinimize)

    problem.objective += pulp.lpSum([instance.stock_cost * stock[p, t]
                                     for p, t in itertools.product(range(n_products), range(n_terms))])

    problem.objective += pulp.lpSum([instance.setup_cost[p][q] * setup[p, q, t]
                                     for p, q, t in itertools.product(range(n_products), range(n_products), range(n_terms))])

    for p in range(n_products):
        problem.addConstraint(stock[p, 0] >= 0)
        problem.addConstraint(stock[p, 0] <= 0)

    for t in range(n_terms):
        problem.addConstraint(pulp.lpSum(
            [production[p, t] for p in range(n_products)]) <= 1)

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

    # last production
    for p in range(n_products):
        problem.addConstraint(last_production[p, 0] >= production[p, 0])
        problem.addConstraint(last_production[p, 0] <= production[p, 0])

    for t in range(1, n_terms):
        problem.addConstraint(pulp.lpSum(
            [last_production[p, t] for p in range(n_products)]) <= 1)
        problem.addConstraint(pulp.lpSum([last_production[p, t] for p in range(
            n_products)]) >= pulp.lpSum([last_production[p, t - 1] for p in range(n_products)]))
        for p in range(n_products):
            problem.addConstraint(
                last_production[p, t] <= last_production[p, t - 1] + production[p, t])
            problem.addConstraint(last_production[p, t] >= production[p, t])

    for p, t in itertools.product(range(n_products), range(1, n_terms)):
        problem.addConstraint(setup[p, p, t] <= 0)

    for p, q, t in itertools.product(range(n_products), range(n_products), range(1, n_terms)):
        if p != q:
            problem.addConstraint(
                setup[p, q, t] >= last_production[p, t - 1] + production[q, t] - 1)

    return problem


def read_instance(filename: str):
    path = os.path.join(instance_dir, filename)
    with open(path) as f:
        n_terms = int(f.readline().replace("\n", ""))
        n_products = int(f.readline().replace("\n", ""))
        demand = []
        for _ in range(n_products):
            l = [int(x) for x in f.readline().replace("\n", "").split(' ')]
            demand.append(l)
        stock_cost = int(f.readline().replace("\n", ""))
        setup_cost = []
        for _ in range(n_products):
            l = [int(x) for x in f.readline().replace("\n", "").split(' ')]
            setup_cost.append(l)

    return Instance(n_products, n_terms, setup_cost, stock_cost, demand)


def main():
    logger.set_logger()
    log = logger.get_logger(__name__)
    instance = read_instance('PSP_100_1.psp')
    stock, production, last_production, setup = make_variables(instance)
    problem = make_problem(instance, stock, production, last_production, setup)
    solve_with_log.exec(problem)

    for t in range(instance.n_terms):
        for p in range(instance.n_products):
            if pulp.value(production[p, t]) == 1:
                log.info(f"product:{t}:{p}")
            if pulp.value(last_production[p, t]) == 1:
                log.info(f"last_production:{t}:{p}")
            if pulp.value(stock[p, t]) >= 1:
                log.info(f"stock:{t}:{p}:{pulp.value(stock[p, t])}")

        for p, q in itertools.product(range(instance.n_products), range(instance.n_products)):
            if pulp.value(setup[p, q, t]) == 1:
                log.info(f"setup:{t}:{p}->{q}")


if __name__ == "__main__":
    main()
