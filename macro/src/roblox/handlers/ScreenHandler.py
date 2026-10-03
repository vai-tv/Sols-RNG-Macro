"""
# SCREEN HANDLER

* handler to ... read the fuckin screen
* contains `ScreenHandler` and child `Clip` which clip readers in `/readers` can parent to access a part of the screen
* picture of the screen at tick, just one! try to avoid duplication when you clip
"""

import mss
import numpy as np
from pathlib import Path

from PIL import Image

from common.HelperFunctions import load_exported_instances
from common.MessageHandler import message
from utils.logger import logging

import pygetwindow as gw  # type: ignore[import-untyped]

def _get_roblox_window() -> gw.Window | None:
    """Returns Roblox window if found, otherwise None."""
    try:
        roblox_windows: list[gw.Window] = [w for w in gw.getAllWindows() if any(keyword in w.title.lower() for keyword in ['roblox', '.roblox'])] # type: ignore
        visible_windows: list[gw.Window] = [w for w in roblox_windows if w.visible]
        
        window = visible_windows[0] if visible_windows else None

    except Exception as e:
        logging.error(f"Error checking for Roblox window: {e}")
        return None

    if window is None:
        logging.error(message('errors', 'roblox', 'no_roblox_window'))
        return None

    return window


class ScreenHandler:

    READERS_DIR = Path(__file__).resolve().parent.parent / "readers"

    def __init__(self):
        self.sct = mss.MSS()
        self.monitor = self.sct.monitors[0] # default to monitor 0... sorry!
        self.frame: np.ndarray | None = None # screenshot

        self.clips: list["Clip"] = []

    def capture_tick(self):
        """Get the screenshot for the current tick, only if Roblox is open."""

        if _get_roblox_window() is None:
            return None
    
        screenshot = self.sct.grab(self.monitor)
        self.frame = np.array(screenshot)

        self.clips = self.load_clips()


    def stop(self):
        """Close the screen handler and release resources."""
        self.sct.close()
        self.frame = None

    def load_clips(self) -> list["Clip"]:
        """Load the clips with the current frame."""
        if self.frame is None:
            logging.warning("Cannot load clips: no frame available.")
            return []

        if not self.clips:
            self.clips = load_exported_instances(
                self.READERS_DIR,
                "roblox.readers",
                Clip,
            )

        for clip in self.clips:
            clip.frame = self.frame
            clip.frame_clip = clip.get_clip(clip.x, clip.y, clip.width, clip.height)
            if clip.frame_clip is not None:
                logging.info(f"Clip at ({clip.x}, {clip.y}) with size ({clip.width}x{clip.height}) loaded.")
            else:
                logging.warning(f"Clip at ({clip.x}, {clip.y}) with size ({clip.width}x{clip.height}) could not be loaded. No frame available.")

        return self.clips

class Clip(ScreenHandler):

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.frame_clip = self.get_clip(x, y, width, height)
        if self.frame_clip is not None:
            logging.info(f"Clip created at ({x}, {y}) with size ({width}x{height}).")
        else:
            logging.warning(f"Clip could not be created at ({x}, {y}) with size ({width}x{height}). No frame available.")

        # if the clip needs it they can load it
        self.PIL_image: Image.Image | None = None

    def get_clip(self, x: int, y: int, width: int, height: int) -> np.ndarray | None:
        """Returns the clipped portion of the screen."""
        if self.frame is None:
            return None
        return self.frame[y:y+height, x:x+width]

    def load_PIL_image(self):
        """Load the clipped portion of the screen as a PIL image."""
        if self.frame_clip is None:
            logging.warning("Cannot load PIL image: no frame available.")
            return
        self.PIL_image = Image.fromarray(self.frame_clip)