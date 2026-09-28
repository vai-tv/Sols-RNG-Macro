"""
# Discord Handler

* this module handles the discord bot, including chat response and communication.
* it contains the discord handler class with important methods for managing the discord bot
* it is needed constantly to manage server commands and discord chat
"""

class DiscordHandler:
    def __init__(self, bot):
        self.bot = bot

    async def send_message(self, channel_id, message):
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(message)