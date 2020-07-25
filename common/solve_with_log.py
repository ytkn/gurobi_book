import pulp
from . import logger


def exec(problem: pulp.LpProblem, is_given_initial_solution: bool, time_limit: int):
    log = logger.get_logger(__name__)
    log.info(f"==========objective=========\n{problem.objective}")
    constraints = "\n".join(
        [f"{k}:{v}" for k, v in problem.constraints.items()])
    log.info(f"=========constraints========\n{constraints}")
    status = problem.solve(pulp.PULP_CBC_CMD(
        msg=True, warmStart=is_given_initial_solution, timeLimit=time_limit))
    log.info(f"status = {pulp.LpStatus[status]}")
    log.info("objective value = {}".format(pulp.value(problem.objective)))
