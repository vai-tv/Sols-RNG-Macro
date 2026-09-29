import os # used to force open client
from PIL import Image, ImageGrab
import pygetwindow as gw  # type: ignore[import-untyped]
import time

import main
from common.MessageHandler import message

from typing import Literal

# install necessary modules from root
from utils.logger import logging
from roblox.handlers.ListenerHandler import ListenerHandler as ListenerHdlr
from roblox.handlers.OverlayHandler import OverlayHandler as OverlayHdlr
# # #
# umm if it aint broke dont fix it ... ik its DRY in main.py but i have bigger issues rn

TICK = 50 #ms

class ClientHandler:

    
    STATUS: Literal["on", "off"] = "off"

    def __init__(self):
        self.listener_handler = ListenerHdlr()
        self.overlay_handler = OverlayHdlr()
        self.start()


    def get_roblox_window(self) -> gw.Window | None:
        """Get the Roblox window."""
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

        # attempt to maximise window and possibly join sols
        if not window.isMaximized:
            window.maximize()
            window.activate()

        return window

    def _get_screenshot(self, window: gw.Window) -> Image.Image | None:
        """Capture the screen area occupied by the Roblox window."""
        try:
            left = int(window.left)
            top = int(window.top)
            right = left + int(window.width)
            bottom = top + int(window.height)

            if right <= left or bottom <= top:
                return None

            return ImageGrab.grab(bbox=(left, top, right, bottom))
        except Exception as error:
            logging.error(f"Unable to capture Roblox window: {error}")
            return None


    def start(self):
        """Start the client handler."""
        if ClientHandler.STATUS == "on":
            logging.warning("Failed to start client, status says it's on!")

        if self.get_roblox_window() is not None:
            logging.info("Found Roblox!")
            self.listener_handler.start()
            ClientHandler.STATUS = "on"

        # try to force client to open through os
        else:
            # find roblox path by walking
            roblox_path = None
            for root, _, files in os.walk("C:\\Users"):
                if any("roblox player" in name.lower() for name in files):
                    roblox_path = os.path.join(root, "roblox player")

                    os.startfile(roblox_path)

            logging.warning("Roblox is not running. Please start Roblox.")
            exit(1)

    def sustain(self):
        """
        Keep the script running while Roblox is active.

        Roblox gameloop!
        """
        
        try:
            while (window := self.get_roblox_window()) is not None:
                time.sleep(TICK * 0.001)
                print('.', end='', flush=True)

                self.overlay_handler.update((int(window.left), int(window.top)))

                ##   MAIN CLIENT LOOP   ##

                screenshot = self._get_screenshot(window)

                ## MAIN CLIENT LOOP END ##

            print()
            logging.info("Roblox has been closed. Exiting script.")
        
        except KeyboardInterrupt:
            print()
            logging.info("Script interrupted by user. Exiting...")
        finally:
            self.listener_handler.stop()
            self.overlay_handler.stop()