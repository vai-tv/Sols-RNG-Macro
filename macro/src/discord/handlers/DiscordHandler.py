"""
# Discord Handler

* this module handles the discord bot, including chat response and communication.
* it contains the discord handler class with important methods for managing the discord bot
* it is needed constantly to manage server commands and discord chat
"""

import discord as disc
import time

from launcher import CONFIG, logging

TOKEN = CONFIG["discord", "BOT_TOKEN"]
print(TOKEN)

class DiscordHandler:
    def __init__(self):
        pass

    def start(self):

        logging.info("Starting Discord...")

    def sustain(self):

        while True:

            time.sleep(0.5)
            pass