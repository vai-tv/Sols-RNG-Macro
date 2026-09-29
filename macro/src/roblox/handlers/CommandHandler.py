"""
# COMMAND HANDLER

* this module is responsible for handling commands entered by the user through `COMMANDOVERLAY.py`.
* it contains a command parser that interprets user input and executes the corresponding actions
* it will receive signals from the overlay and respond based on commands found in the commands sibing folder
"""

import tkinter as tk
from tkinter import ttk

__all__ = ["CommandOverlay"]


class CommandOverlay(ttk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.command = ttk.Entry(self)
        self.command.pack()