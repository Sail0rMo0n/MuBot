import subprocess
import sys
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
from Client.events import EventsListener

bot = None
intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.voice_states = True

def main():
    load_dotenv()
    global bot
    bot = commands.Bot(
        command_prefix = "!",
        intents = intents
    )
    EventsListener(bot)
    bot.run(
        token = os.getenv('DISCORD_TOKEN')
    )

if __name__ == '__main__':
    main()