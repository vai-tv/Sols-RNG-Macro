"""
# CLIENT HANDLER

* oh yes here it comes
* manages the client, starts it, keeps it running, and handles the main loop
* contains `ClientHandler` which is the main class for the client
    * also has a `RobloxWindowHandler` class which is used to find and launch the Roblox client
* also inherits pretty much all handlers... may need to generalise that soon
"""

import os # used to force open client
import pygetwindow as gw  # type: ignore[import-untyped]
import requests
import time
import urllib.parse
import webbrowser

from typing import Literal, Protocol, TypedDict

from common.config import Config
from utils.logger import logging

from roblox.handlers.ListenerHandler import ListenerHandler as ListenerHdlr
from roblox.handlers.OverlayHandler import OverlayHandler as OverlayHdlr
from roblox.handlers.ScreenHandler import ScreenHandler as ScreenHdlr, _get_roblox_window


TICK = 500 #ms
timeout_attempts = 3 # try to start 3 times before giving up
timeout_base_wait = 4 # seconds, increase by 2x each timeout

class RobloxWindowHandler:
    """Find, launch, and connect to the Roblox client."""


    @staticmethod
    def get_roblox_window() -> gw.Window | None:
        """
        Get and maximise the Roblox window if it exists, otherwise return None.
        """

        window = _get_roblox_window()
        if window is None:
            return None

        if not window.isMaximized:
            window.maximize()
            window.activate()
        return window

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

    def attempt_web_connect(self) -> bool:
        """
        Tries to connect to Sols RNG through the web.

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

        logging.info("Trying to connect to Sols RNG through your browser... please be patient.")

        return webbrowser.open(URL)

    STATUS: Literal["on", "off"] = "off"
    
    def start(self) -> bool:
        """
        Starts the Roblox player and attempts to join the configured Sols RNG server.
        
        Returns:
            bool: success status, go figure
        """

        # get the roblox window if it exists
        if self.get_roblox_window() is not None:
            logging.info("Found Roblox!")

            # try to connect to Sols RNG through the web
            # if it fails, warn the user and return False
            if self.attempt_web_connect():
                return True
            logging.warning("Failed to connect to Sols RNG through your browser. Please check your .ROBLOSECURITY cookie and try again.")
            return False

        # since the roblox window doesn't exist, try to open it
        logging.info("Roblox is not running. Attempting to start Roblox... you may have to restart the script.")
        for root, _, files in os.walk("C:\\Users"):
            # if the roblox player is not in this directory, continue searching
            if not any("roblox player" in name.lower() for name in files):
                continue

            # start roblox through os
            roblox_path = os.path.join(root, "roblox player")
            os.startfile(roblox_path)

            # timeout, then attempt a recursive start
            time.sleep(10)
            return self.start()

        return False

    def run_boot_wrapper(self):
        """
        Wrapper to start the window.
        Either successfully boots Sols RNG or exits.

        Also sets the STATUS to "on" if successful.
        """

        if self.STATUS == "on":
            logging.warning("Client is already running.")
            return

        for i in range(timeout_attempts):
            if self.start():
                self.STATUS = "on"
                logging.info("Successfully started window!")
                return
            logging.warning(f"Failed to start! Trying again ({i + 1}/{timeout_attempts})...")
            # x2 timeout each time
            time.sleep(timeout_base_wait * (2 ** i))

        logging.fatal(f"Failed to start client after {timeout_attempts} attempts. Exiting...")
        exit(1)


class _Handlers(TypedDict):
    listener: ListenerHdlr
    overlay: OverlayHdlr
    screen: ScreenHdlr

# since in ClientHandler.stopallhandlers() we want to stop all handlers, we can define a protocol for them to implement a stop() method
class _Handler(Protocol):
    def stop(self) -> None: ...

class ClientHandler:

    def __init__(self):
        self.window_handler = RobloxWindowHandler()
        self.window_handler.run_boot_wrapper()

        # i kindly request that all listeners start on init! teehee
        self.handlers: _Handlers = {
            "listener": ListenerHdlr(),
            "overlay": OverlayHdlr(),
            "screen": ScreenHdlr()
        }

    def stopallhandlers(self) -> None:
        """
        Stop all handlers.
        """

        # sorry i hate this type annotation!!
        handlers: tuple[_Handler, ...] = (
            self.handlers["listener"],
            self.handlers["overlay"],
            self.handlers["screen"],
        )
        for handler in handlers:
            handler.stop()
        logging.info(f"Stopped all {len(handlers)} handlers.")

    def sustain(self):
        """
        Keep the script running while Roblox is active.

        Roblox gameloop!
        """
        
        try:
            while (window := self.window_handler.get_roblox_window()) is not None:
                time.sleep(TICK * 0.001)
                print('.', end='', flush=True)

                ##   MAIN CLIENT LOOP   ##

                # handlers go!
                # self.listener is already listening!
                position = (int(window.left), int(window.top))
                self.handlers["overlay"].update(position)
                self.handlers["screen"].capture_tick()

                ## MAIN CLIENT LOOP END ##

            print()
            logging.info("Roblox has been closed. Exiting script.")

        ## EXIT PROCEDURE ##
        
        except KeyboardInterrupt:
            print()
            logging.info("Script interrupted by user. Exiting...")
        except Exception as e:
            print()
            logging.fatal(f"Umm! An unexpected error occurred: {e}")
        finally:
            self.stopallhandlers()