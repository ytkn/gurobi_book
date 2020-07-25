import logging


def set_logger():
    logging.basicConfig(
        format='%(asctime)s:[%(levelname)s]:<%(name)s:%(funcName)s>:%(message)s')


def get_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    return log
