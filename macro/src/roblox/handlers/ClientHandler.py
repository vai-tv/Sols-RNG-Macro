import logging
import pygetwindow as gw  # type: ignore[import-untyped]
import time

class ClientHandler:

    def __init__(self):
        self.start()

    def get_roblox_wndow(self) -> gw.Window | None:
        """Get the Roblox window."""
        try:
            roblox_windows: list[gw.Window] = [w for w in gw.getAllWindows() if any(keyword in w.title.lower() for keyword in ['roblox', '.roblox'])] # type: ignore
            visible_windows: list[gw.Window] = [w for w in roblox_windows if w.visible]
            
            return visible_windows[0] if visible_windows else None
            
        except Exception as e:
            logging.error(f"Error checking for Roblox window: {e}")
            return None

    def start(self):
        """Start the client handler."""
        if self.get_roblox_wndow() is not None:
            logging.info("Found Roblox!")
        else:
            logging.warning("Roblox is not running. Please start Roblox.")
            exit(1)

    def sustain(self):
        """Keep the script running while Roblox is active."""
        try:
            while True:
                if self.get_roblox_wndow() is None:
                    logging.info("Roblox has been closed. Exiting script.")
                    break
                time.sleep(0.5)
                print('.', end='', flush=True)  # Print a dot to indicate the script is still running
        except KeyboardInterrupt:
            logging.info("Script interrupted by user. Exiting...")