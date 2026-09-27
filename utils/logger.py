import logging

def setup_logger():
    """Set up the logger for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(".logs/launcher.log"),
            logging.StreamHandler()
        ]
    )
    logging.info("Logger initialized.")