"""
# LISTENER HANDLER

* listens to keyboard and mouse input by the user (then sends to a respective handler)
* provides a listener class that the listener can use
* manages everything in `\\listeners` with `self.listeners` list
"""

import importlib
import os

from pathlib import Path

from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode

from typing import Literal


from main import logging


class Listener:

    """
    Main `Listener` class.
    * has a keychar / mousebutton variable to listen to
    """

    def __init__(self, keychar: str | None = None, mousebutton: str | None = None) -> None:

        # key / mouse selection
        if keychar is not None and mousebutton is not None:
            raise TypeError(f"Conflicting listener types {keychar} key and {mousebutton} mouse.")
        
        if keychar is not None:
            self.keychar = keychar
            self.key = self._keycode(keychar)
            self.type: Literal["key", "mouse"] = "key"
        elif mousebutton is not None:
            self.mousebutton = mousebutton
            self.type: Literal["key", "mouse"] = "mouse"

        else:
            raise TypeError(f"Listener needs either key or mouse argument specified.")

        self.listener = keyboard.Listener(on_press=self.handle) if self.type == "key" else mouse.Listener(on_click=self.handle)

    @property
    def exit_requested(self) -> bool:
        return False

    @staticmethod
    def _keycode(keychar: str):
        """Helper to safely resolve both standard characters and special keys."""

        # special key names defined in pynput ("space", "enter", "f1")
        if hasattr(Key, keychar.lower()):
            return getattr(Key, keychar.lower())
        
        #  normal character keys ("1", "a")
        return KeyCode.from_char(keychar)

    def start(self) -> None:
        """Starts the listener and sets status."""

        try:
            logging.info("Starting listeners...")
            self.listener.run()

        except Exception as e:
            raise e
        else:
            self.status = "on"

    def handle(self) -> bool | None:
        """Should be replaced by the user."""

        raise NotImplementedError(f"Listener {self.type.capitalize()} has no handle function!")

    def stop(self) -> None:
        self.listener.stop()
      

class ListenerHandler:

    LISTENERS_DIR = os.path.join(os.path.dirname(__file__), "listeners")

    def __init__(self):
        self.listeners = self.load_listeners()
        self.start()

    def start(self) -> None:
        """
        Start the main listener and connect keybinds to sublisteners.
        """

        for listener in self.listeners:
            logging.info(f"Starting {listener.__class__.__name__}..")

            # bind keybind to listener
            listener.start()
            

    def stop(self) -> None:
        """
        Stop the main listener and sublisteners.
        """

        for listener in self.listeners:
            listener.stop()

    @staticmethod
    def load_listeners() -> list["Listener"]:
        """
        Creates configured listener instances.

        Returns
        list["Listener"]: All listeners as a list.
        """

        loaded_listeners = []
        listeners_dir = Path(__file__).resolve().parent / "listeners"

        for file_path in listeners_dir.glob("*.py"):
            if file_path.name == "__init__.py":
                continue

            module_name = file_path.stem
            full_module_path = f"roblox.listeners.{module_name}"
            
            module = importlib.import_module(full_module_path)
            
            if not hasattr(module, "__all__"):
                logging.warning(f"Couldn't load listener {listeners_dir} since it has no __all__.")
                continue

            for class_name in module.__all__:
                listener_class = getattr(module, class_name)

                instance = listener_class()
                
                loaded_listeners.append(instance)
                logging.info(f"Listener added! {file_path}")

        return loaded_listeners
