"""
# MESSAGE HANDLER

* handle messages.json
* contains message() function which takes a `*message_location` and  `**variables`
* used mainly in logging
"""

import json
import os
import pathlib

# load messages.json
MESSAGES_PATH = os.path.join(pathlib.Path.cwd(), "macro", "src", "common", "messages.json")
with open(MESSAGES_PATH, "r", encoding="utf-8") as f:
    MESSAGES: dict = json.load(f)

def message(*message_location: str, **variables: str) -> str:
    """
    Accesses a message from messages.json and replace variables.
    
    Args:
    message_location (str): path to the message
    variables (dict[str, str]): variables to substitute (named by key)

    Returns:
    str: the fully formatted message
    """

    messages_copy: dict = MESSAGES.copy() # copy so we don't affect MESSAGES

    # get the message content using the specified path
    for directory in message_location:
        try:
            messages_copy = messages_copy[directory]
        except KeyError:
            raise KeyError(f"Tried to access a missing message '{directory}' in {MESSAGES}.")

    target_message: str = messages_copy # type: ignore

    # replace variables from kwargs
    for [name, value] in variables.items():
        target_message = target_message.format(value, name)

    return target_message

