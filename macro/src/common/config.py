import json
import logging
import pathlib
from typing import Any

from os import path

from macro.src.common.MessageHandler import message

CONFIG_PATH = path.join(pathlib.Path.cwd(), "config.json")

important_config = [
    ("discord", "BOT_TOKEN"),
]

class ConfigManager:

    data: dict[str, Any] = {}

    def __init__(self):
        self.data = ConfigManager.data if ConfigManager.data else ConfigManager.load()
        ConfigManager.data = self.data

    def __getitem__(self, key: tuple[str, ...]) -> Any:
        value = self.data
        for directory in key:
            value = value[directory]
        return value

    # sorry for poo typing
    @staticmethod
    def load() -> dict[str, Any]:
        """
        Loads config file with JSON at startup. Also checks for key constants and raises necessary errors.
        Returns JSON dict.
        """

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        config_walker = config.copy()

        # check for important config presence
        for location in important_config:
            for directory in location:
                try:
                    config_walker = config_walker[directory]
                except KeyError:
                    raise KeyError(f"Tried to look for a missing important config variable '{directory}' in {config}.")

                # raise logging error if the important config couldn't be found
                if not config_walker:
                    logging.error(message('errors', 'missing_config', variable_name=directory))

        return config