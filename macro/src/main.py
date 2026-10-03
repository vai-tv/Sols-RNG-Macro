import sys
from pathlib import Path

# force import to root im sorry!
SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
# # #


def main():
    from roblox.handlers.ClientHandler import ClientHandler
    from discord.handlers.DiscordHandler import DiscordHandler

    client = ClientHandler()
    client.sustain()

    # discord = DiscordHandler()
    # discord.sustain()

if __name__ == '__main__':
    main()