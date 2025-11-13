import os
import logging
import sys


def get_logger(name: str):
    """
    Returns a centralized logger.
    """
    logger = logging.getLogger(name)

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()  # default INFO

    if not logger.handlers:
        logger.setLevel(getattr(logging, log_level))

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(getattr(logging, log_level))

        formatter = logging.Formatter('%(asctime)s  |  %(name)-35s:%(lineno)-4d  |  %(levelname)-8s  |  %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger
