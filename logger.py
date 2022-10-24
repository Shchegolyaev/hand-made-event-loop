import logging
import sys

logging.basicConfig(
    # filename="tasks_logs.log",
    stream=sys.stdout,
    format="%(asctime)s %(message)s",
    # filemode="w",
    # format="%(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
