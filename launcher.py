"""
# LAUNCHER

* this module launches the game when run.
* it checks for updates from the GitHub repository and applies them if available.
* this is the start of the workflow and the first module to be run when the program is executed.
"""

import logging
import io
import os
import subprocess
import shutil
import sys
import requests
import zipfile

from utils.constants import Git
from utils.logger import setup_logger

from macro.src.common.config import Config

setup_logger()

def get_latest_release() -> tuple[str, str] | None:
    """
    Attempt to fetch the latest release information from GitHub, with a fallback to prerelease.
    Returns:
        tuple[str, str]: A tuple containing the latest version tag and the zipball URL.
    If no release information is found, returns None.
    """
    headers = {"User-Agent": "Sols-RNG-Macro"}
    try:
        response = requests.get(Git.URL, headers=headers, timeout=10)
        # logic gate for 200 and other status codes
        if response.status_code == 200:
            latest_release = response.json()
            return latest_release['tag_name'], latest_release['zipball_url']
        
        logging.warning("Failed to find a stable release. Checking for prereleases...")
        releases_url = Git.URL.rsplit("/", 1)[0]
        prerelease_response = requests.get(releases_url, headers=headers, timeout=10)
        if prerelease_response.status_code == 200:
            prereleases = [
                release for release in prerelease_response.json()
                if release.get("prerelease")
            ]
            if prereleases:
                prerelease = prereleases[0]
                return prerelease['tag_name'], prerelease["zipball_url"]
        logging.warning("No releases found on GitHub yet. Skipping update check.")
    except Exception as e:
        logging.error(f"An error occurred while fetching the latest release: {e}")

    return None

def download_and_apply_update(zipball_url: str):
    """Download the source code zipball, extract it, overwrite project files, and restart."""
    logging.info("Downloading source code update...")
    headers = {"User-Agent": "Sols-RNG-Macro"}
    
    try:
        res = requests.get(zipball_url, headers=headers, timeout=30)
        if res.status_code != 200:
            logging.error("Failed to download update zip package.")
            return

        # extract zip from memory
        with zipfile.ZipFile(io.BytesIO(res.content)) as z:

            root_dir_in_zip = z.namelist()[0]
            extract_path = os.path.join(os.getcwd(), "update_temp")
            z.extractall(extract_path)

            source_extracted = os.path.join(extract_path, root_dir_in_zip)

            # copy updated files over current directory structure
            for item in os.listdir(source_extracted):
                s = os.path.join(source_extracted, item)
                d = os.path.join(os.getcwd(), item)
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

            # clean up temporary extraction folder
            shutil.rmtree(extract_path)

        logging.info("Update applied successfully! Restarting launcher...")
        # restart the script with the exact same arguments
        os.execv(sys.executable, [sys.executable] + sys.argv)

    except Exception as e:
        logging.error(f"Failed to apply update: {e}. Launching current version...")

def launch_main():
    """Launch the macro script using subprocess."""
    try:
        print()
        logging.info("Launching...")
        subprocess.run([sys.executable, "macro/src/main.py"], check=True)
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(f"Module not found! {e.with_traceback}")
    except subprocess.CalledProcessError as e:
        logging.fatal("[WARNING] An unknown error occured with the main file!")
        logging.fatal(f"Failed to launch main.py: {e}")


def start():

    # check for updates
    print()
    logging.info(f"Checking for the latest release from {Git.URL}...")

    latest_release_info = get_latest_release()

    if latest_release_info is None:
        logging.info("Could not retrieve the latest release information. Launching current version...")
        return
    
    latest_version, zipball_url = latest_release_info
    logging.info(f"Latest Github release: {latest_version} | Running version: {Git.VERSION}")

    # compare versions and decide whether to update or launch the current version
    if latest_version == Git.VERSION:
        logging.info("You are already on the latest version.")
        return

    elif latest_version < Git.VERSION:
        logging.warning(f"You are running a newer version ({Git.VERSION}) than the latest release ({latest_version}). Did you build from source? Launching current version...")
        return
    
    logging.info(f"New version available ({latest_version})! Preparing source code update...")
    download_and_apply_update(zipball_url)

if __name__ == "__main__":
    start()
    launch_main()