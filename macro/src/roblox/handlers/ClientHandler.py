import os # used to force open client
from PIL import Image, ImageGrab
import pygetwindow as gw  # type: ignore[import-untyped]
import requests
import time
import urllib.parse
import webbrowser

import main
from common.MessageHandler import message

from typing import Literal

# install necessary modules from root
from utils.logger import logging
from roblox.handlers.ListenerHandler import ListenerHandler as ListenerHdlr
from roblox.handlers.OverlayHandler import OverlayHandler as OverlayHdlr
# # #
# umm if it aint broke dont fix it ... ik its DRY in main.py but i have bigger issues rn

from common.config import Config

TICK = 50 #ms
timeout_attempts = 3 # try to start 3 times before giving up
timeout_base_wait = 4 # seconds, increase by 2x each timeout

class ClientHandler:

    
    STATUS: Literal["on", "off"] = "off"

    def __init__(self):
        self.listener_handler = ListenerHdlr()
        self.overlay_handler = OverlayHdlr()

        self.boot_or_exit()

    def _get_roblox_window(self) -> gw.Window | None:
        """
        Helper to get the Roblox window.
        
        Also attempts to start Roblox if it is not running.
        """
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

    PLACE_ID = 15532962292
    ROBLOSECURITY_COOKIE = Config("roblox", ".ROBLOSECURITY_cookie")

    def _get_private_server_code(self) -> str | None:
        """
        Helper to obtain the first private server available for the Sols RNG client.
        """

        URL = f"https://games.roblox.com/v1/games/{self.PLACE_ID}/private-servers"

        headers = {
            "Cookie" : f".ROBLOSECURITY={self.ROBLOSECURITY_COOKIE.data}"
        }

        response = requests.get(URL, headers=headers)

        if response.status_code == 200:
            data = response.json()
            # first private server code is in /data[0]/accessCode
            access_code = data["data"][0]["accessCode"]
            return access_code
        else:
            logging.error(f"Failed to fetch private servers: {response.status_code}")
        return None

    def _attempt_web_connect(self) -> bool:
        """
        Helper to try connect to Sols RNG through the web.

        Returns:
        bool: success status, go figure
        """

        base_url = "roblox://experiences/start"

        params = {
            "placeId": self.PLACE_ID,
            # by default connect to first available private server
            "accessCode": self._get_private_server_code()
        }

        query = urllib.parse.urlencode(params)
        URL = f"{base_url}?{query}"

        logging.info("Trying to connect to Sols RNG... please be patient.")

        return webbrowser.open(URL)

    def start(self) -> bool:
        """Start the client handler.
        
        Returns:
        bool: success status
        """

        # obviously don't start client if it's already on
        if ClientHandler.STATUS == "on":
            logging.warning("Didn't start client, status says it's on!")
            return False

        # found roblox window, try to join Sols
        if self._get_roblox_window() is not None:
            logging.info("Found Roblox!")

            if self._attempt_web_connect(): # try to join Sols
                self.listener_handler.start()
                return True

        # nevermind, try to force client to open through os
        # find roblox path by walking
        roblox_path = None
        for root, _, files in os.walk("C:\\Users"):
            if not any("roblox player" in name.lower() for name in files):
                continue

            roblox_path = os.path.join(root, "roblox player")
            os.startfile(roblox_path)

            # try to restart after a moment
            time.sleep(10)
            if self.start():
                return True

        logging.warning("Roblox is not running. Please start Roblox.")
        return False

    def boot_or_exit(self):
        """
        Either successfully boots Sols RNG or exits.
        """

        for i in range(timeout_attempts):
            if self.start():
                self.STATUS = "on"
                return True
            logging.warning(f"Failed to start! Trying again ({i + 1}/{timeout_attempts})...")
            # x2 timeout each time
            time.sleep(timeout_base_wait * (2 ** i))

        logging.fatal(f"Failed to start client after {timeout_attempts} attempts. Exiting...")
        exit(1)

    def sustain(self):
        """
        Keep the script running while Roblox is active.

        Roblox gameloop!
        """
        
        try:
            while (window := self._get_roblox_window()) is not None:
                time.sleep(TICK * 0.001)
                print('.', end='', flush=True)

                try:
                    position = (int(window.left), int(window.top))
                except gw.PyGetWindowException:
                    continue

                self.overlay_handler.update(position)

                ##   MAIN CLIENT LOOP   ##

                screenshot = self._get_screenshot(window)

                # ScreenReaders managed by a ScreenManager can then access segments of the screenshot
                # through ScreenManager().process(screenshot)
                # which contains the internal loop for ScreenReaders and text processing

                ## MAIN CLIENT LOOP END ##

            print()
            logging.info("Roblox has been closed. Exiting script.")
        
        except KeyboardInterrupt:
            print()
            logging.info("Script interrupted by user. Exiting...")
        finally:
            self.listener_handler.stop()
            self.overlay_handler.stop()