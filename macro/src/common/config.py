import json
import logging
import pathlib
from typing import Any, TypeAlias

from os import path

from macro.src.common.MessageHandler import message

CONFIG_PATH = path.join(pathlib.Path.cwd(), "config.json")

important_config = [
    ("discord", "BOT_TOKEN"),
]
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config_file = json.load(f).copy()

# Source - https://stackoverflow.com/a/76646986
# Posted by pradyunsg
# Retrieved 2026-09-29, License - CC BY-SA 4.0
JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


class Config:

    def __init__(self, *home_key: str):
        self.data: JSON = self.load()

        for directory in home_key:
            self.data = self.data[directory]  # type: ignore[index]

    def __str__(self) -> str:
        return str(self.data)

    def __getitem__(self, *key: str) -> JSON:
        # only copy data if it's a dict, not str
        data = self.data if not isinstance(self.data, dict) else self.data.copy()

        print(f"{key=}")
        for directory in key[0]:
            try:
                if not isinstance(data, str):
                    raise TypeError(f"Directory {directory} must be a str!")
                data = data[directory] # type: ignore
            except Exception as e:
                logging.error(f"Couldn't get config from directory {directory} {data}: {e}")
                exit(1)
        return data

    @staticmethod
    def load() -> JSON:
        """
        Loads config file at startup. Also checks for key constants and raises necessary errors.
        """
        config_walker = config_file.copy()

        # check for important config presence
        for location in important_config:
            for directory in location:
                try:
                    config_walker = config_walker[directory]
                except KeyError:
                    raise KeyError(f"Tried to look for a missing important config variable '{directory}' in {config_file}.")

                # raise logging error if the important config couldn't be found
                if not config_walker:
                    logging.error(message('errors', 'missing_config', variable_name=directory))

        return config_file