import json
import logging
import pathlib

from os import path

from macro.src.common.MessageHandler import message

CONFIG_PATH = path.join(pathlib.Path.cwd(), "config.json")

important_config = [
    ("discord", "BOT_TOKEN"),
]

class Config:

    def __init__(self):
        self.data = self.load()

    def __getitem__(self, key):
        return self.data[key]

    # sorry for poo typing
    def load(self) -> dict[str, str | dict]:
        """
        Loads config file with JSON at startup. Also checks for key constants and raises necessary errors.
        Returns JSON dict.
        """

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        # check for important config presence
        for location in important_config:
            for directory in location:
                try:
                    config = config[directory]
                except KeyError:
                    raise KeyError(f"Tried to look for a missing important config variable '{directory}' in {config}.")

                # raise logging error if the important config couldn't be found
                if not config:
                    logging.error(message('errors', 'missing_config', variable_name=directory))

        return config

CONFIG = Config()