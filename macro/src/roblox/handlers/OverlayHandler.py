"""
# OVERLAY HANDLER

this module handles individual overlays contained in the overlays/ sibling folder. each overlay is a class that inherits from OverlayHandler and implements the required methods.
it contains the OverlayHandler class which is the base class for all overlays.
this module is used in OverlayManager.py to manage the overlays and their updates.
"""

import tkinter as tk

class Overlay(tk.Tk):
    """The single borderless Tk window used to display overlay text."""

    TRANSPARENT_COLOR = "#010203"

    def __init__(self) -> None:
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=self.TRANSPARENT_COLOR)
        self.wm_attributes("-transparentcolor", self.TRANSPARENT_COLOR)

        self.text = tk.Label(
            self,
            text="",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg=self.TRANSPARENT_COLOR,
            anchor="w",
        )
        self.text.pack()
        self.geometry("+20+40")


class OverlayHandler:
    """Own and update the one shared text overlay window."""

    def __init__(self) -> None:
        self.window = Overlay()
        self.closed = False

    def set_text(self, text: str) -> None:
        self.window.text.configure(text=text)
        self.window.update_idletasks()

    def update(self, position: tuple[int, int] | None = None) -> None:
        if self.closed:
            return

        if position is not None:
            x, y = position
            self.window.geometry(f"+{x + 16}+{y + 38}")

        try:
            self.window.update()
        except tk.TclError:
            self.closed = True

    def stop(self) -> None:
        if not self.closed:
            self.window.destroy()
            self.closed = True
