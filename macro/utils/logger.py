import logging
import os

def setup_logger():
    """Set up the logger for the application."""

    if not os.path.exists(".logs"):
        os.makedirs(".logs")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s %(filename)s] %(message)s",
        handlers=[
            logging.FileHandler(".logs/launcher.log"),
            logging.StreamHandler()
        ],
        force=True
    )

setup_logger()