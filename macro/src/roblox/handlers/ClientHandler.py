import os # used to force open client
import pygetwindow as gw  # type: ignore[import-untyped]
import time

import main
from common.MessageHandler import message

# install necessary modules from root
from utils.logger import logging
from roblox.ListenerManager import ListenerManager
# # #
# umm if it aint broke dont fix it ... ik its DRY in main.py but i have bigger issues rn

class ClientHandler:

    def __init__(self):
        self.listener_manager = ListenerManager()
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
        
        window.maximize()
        window.activate()
        return window

    def start(self):
        """Start the client handler."""

        if self.get_roblox_window() is not None:
            logging.info("Found Roblox!")
            self.listener_manager.start()

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
        """Keep the script running while Roblox is active."""
        try:
            while True:
                if self.get_roblox_window() is None:
                    print()
                    logging.info("Roblox has been closed. Exiting script.")
                    break
                time.sleep(0.5)
                print('.', end='', flush=True)  # Print a dot to indicate the script is still running
        except KeyboardInterrupt:
            print()
            logging.info("Script interrupted by user. Exiting...")
        finally:
            self.listener_manager.stop()