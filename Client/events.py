import os
import discord
from discord.app_commands import tree

def EventsListener(bot):
    @bot.event
    async def on_ready() -> None:
        print(f"{bot.user.name} has connected to Discord.")
        print("Syncing...")
        try:
            await bot.tree.sync()
            print("Sync completed")
        except discord.HTTPException:
            pass

    @bot.event
    async def setup_hook() -> None:
        print("Loading cogs")
        for filename in os.listdir('./Cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                await bot.load_extension(name=f'Cogs.{filename[:-3]}')