import json
import logging
import os
import subprocess
import sys
import urllib.request
import requests

from utils.constants import Git
from utils.logger import setup_logger

def get_latest_release() -> tuple[str, list[dict]]:
    try:
        response = requests.get(Git.URL, timeout=5)
        if response.status_code == 200:
            latest_release = response.json()
            return latest_release['tag_name'], latest_release['assets']
        elif response.status_code == 404:
            logging.warning("No releases found on GitHub yet. Skipping update check.")
        else:
            logging.error(f"Failed to fetch the latest release. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"An error occurred while fetching the latest release: {e}")
    
    return None, []

def launch_main():
    """Launch the main.py script using subprocess."""
    try:
        print()
        logging.info("Launching main.py...")
        # Use Popen or run depending on whether you want the launcher to stay open or close
        subprocess.run([sys.executable, "macro/src/main.py"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to launch main.py: {e}")

def main():

    # setup logging
    setup_logger()

    # check for updates
    logging.info(f"Checking for the latest release from {Git.URL}...")
    latest_version, assets = get_latest_release()

    if not latest_version:
        logging.info("Could not retrieve the latest release information. Launching current version...")
        launch_main()
        return
    logging.info(f"Latest Github release: {latest_version} | Running version: {Git.VERSION}")

    # compare versions and decide whether to update or launch the current version
    if latest_version == Git.VERSION:
        logging.info("You are already on the latest version.")
        launch_main()
        return

    elif latest_version < Git.VERSION:
        logging.warning(f"You are running a newer version ({Git.VERSION}) than the latest release ({latest_version}). Did you build from source? Launching current version...")
        launch_main()
        return
    
    logging.info(f"New version available ({latest_version})! Preparing update...")
    target_asset_name = "main.exe" if sys.platform == "win32" else "main_mac"

    # find the download URL for the appropriate asset based on the platform
    download_url = [asset['browser_download_url'] for asset in assets if asset['name'] == target_asset_name][0]

    if not download_url:
        logging.warning(f"No matching asset found for your platform ({target_asset_name}). Launching current version...")
        launch_main()
        return

    temp_path = os.path.join(os.path.expanduser("~"), target_asset_name)
    logging.info(f"Downloading update from {download_url}...")
    
    try:
        urllib.request.urlretrieve(download_url, temp_path)

        # send to updater_helper.py to handle the file swap and restart
        subprocess.Popen([
            sys.executable,
            "updater_helper.py",
            os.path.abspath("main.py"),
            temp_path
        ])
        sys.exit()

    except Exception as e:
        logging.error(f"Download failed: {e}. Launching current version...")

    launch_main()

if __name__ == "__main__":
    main()