import os
from typing import Literal
# from typing import Any, Literal, Optional
import discord
from discord.ext import commands
from discord import app_commands, ui
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import fitz
from datetime import date, datetime, timezone
from io import BytesIO
from cogs.linkcog import LinkCog
from cogs.filecog import FileCog
from cogs.itemcog import ItemCog
from cogs.modulecog import ModuleCog
from cogs.musiccog import MusicCog
from cogs.announcementcog import AnnouncementCog
from glot import Glot
import authenticate
# import requests
# import re
# import markdown
# from extensions import StrikethroughExtension
import sys

debug = True
if (len(sys.argv) > 2):
    print(f"Usage: python {sys.argv[0]} [guild:0|1]\n\tguild = 0: Test Server (default)\n\tguild = 1: PMGC Server", flush=True)
    sys.exit()
elif (len(sys.argv) == 2):
    if (sys.argv[1] == '1'): debug = False
    elif (sys.argv[1] == '0'): pass
    else:
        print(f"Usage: python {sys.argv[0]} [guild:0|1]\n\tguild = 0: Test Server (default)\n\tguild = 1: PMGC Server", flush=True)
        sys.exit()



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot_intents = discord.Intents.all()
bot_intents.message_content = True
bot_intents.guilds = True
bot_intents.guild_messages = True
bot_intents.members = True
# bot = commands.Bot(command_prefix = '!', intents=bot_intents)
bot = Glot(command_prefix = '!', intents=bot_intents)

guildPMGC = None
guildTest = None

group = app_commands.Group(name='commands', description='Work with the bot commands in bulk')

# Command to sync application commands
@group.command(name="sync", description="Syncs all Slash- and Context Menu- Commands")
async def sync(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    globalResults = await bot.tree.sync(guild=None)
    guildResults = await bot.tree.sync(guild=bot.currentGuild)
    await interaction.followup.send(f"Synced the following global commands: {globalResults}\nSynced the following guild commands: {guildResults}")

# Command to clear application commands
@group.command(name="clear", description="Clears all Slash- and Context Menu- Commands")
async def clear(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync(guild=None)
    await interaction.followup.send(f"Cleared commands")

# Command to list application commands
@group.command(name="list", description="Lists all Slash-, Context Menu-, and Prefix- Commands")
async def list_commands(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    appcmds = bot.tree.get_commands(guild=bot.currentGuild)
    result = '## App Commands:'
    for cmd in appcmds:
        if isinstance(cmd, app_commands.Command):
            result = result + f'\n* `{cmd.name}`'
        elif isinstance(cmd, app_commands.ContextMenu):
            result = result + f'\n* `{cmd.name}` — Context Menu'
        elif isinstance(cmd, app_commands.Group):
            result = result + f'\n* `{cmd.name}`:'
            for subcmd in cmd.commands:
                if isinstance(subcmd, app_commands.Command):
                    result = result + f'\n  * `{subcmd.name}`'
                elif isinstance(subcmd, app_commands.Group):
                    result = result + f'\n  * `{subcmd.name}`:'
                    for subsub in subcmd.commands:
                        result = result + f'\n    * `{subsub.name}`'
    cmds = bot.commands
    result = result + '\n## Prefix Commands:'
    for cmd in cmds:
        if isinstance(cmd, commands.Command):
            result = result + f'\n* `!{cmd.name}`'
        if isinstance(cmd, commands.Group):
            result = result + f'\n* `!{cmd.name}`:'
            for subcmd in cmd.commands:
                result = result + f'\n  * `{subcmd.name}`'
    await interaction.followup.send(result)

# @client.event
@bot.event
async def on_ready():
    guildPMGC = bot.get_guild(os.getenv('GUILD_ID'))
    guildTest = bot.get_guild(1378895395253387344)

    bot.tree.clear_commands(guild=None)

    bot.defaultURL = os.getenv('DEFAULT_URL')
    bot.glanvasURL = bot.glanvasURL if bot.glanvasURL != '' else bot.defaultURL

    bot.defaultCalId = os.getenv('DEFAULT_CALENDAR_ID')
    bot.calendarId = bot.calendarId if bot.calendarId != '' else bot.defaultCalId

    bot.default_roster_id = os.getenv('DEFAULT_ROSTER_ID')
    bot.roster_id = bot.roster_id if bot.roster_id != '' else bot.default_roster_id

    bot.setGuild(guildTest if debug else guildPMGC)
    group._guild_ids = [bot.currentGuild.id]

    try:
        await bot.load_extension("glanvascog")
        print(f'Loaded extension: glanvascog')
    except commands.ExtensionAlreadyLoaded:
        print(f'Extension already loaded: glanvascog')
    except commands.ExtensionNotFound:
        print(f'Extension not found: glanvascog')
    except Exception as e:
        print(f'Failed to load extension glanvascog. Reason: {e}')

    for filename in os.listdir('cogs'):
        if (filename.endswith('cog.py')):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded Cog: {filename[:-3]}')
            except commands.ExtensionAlreadyLoaded:
                print(f'Cog already loaded: {filename[:-3]}')
            except commands.ExtensionNotFound:
                print(f'Cog not found: {filename[:-3]}')
            except Exception as e:
                print(f'Failed to load Cog {filename[:-3]}. Reason: {e}')

    
    for filename in os.listdir("extensions"):
        if (filename.endswith(".py")):
            try:
                await bot.load_extension(f'extensions.{filename[:-3]}')
                print(f'Loaded extension: {filename[:-3]}')
            except commands.ExtensionAlreadyLoaded:
                print(f'Extension already loaded: {filename[:-3]}')
            except commands.ExtensionNotFound:
                print(f'Extension not found: {filename[:-3]}')
            except Exception as e:
                print(f'Failed to load extension {filename[:-3]}. Reason: {e}')

    try:
        await bot.load_extension("loadercog")
        print(f'Loaded extension: loadercog')
    except commands.ExtensionAlreadyLoaded:
        print(f'Extension already loaded: loadercog')
    except commands.ExtensionNotFound:
        print(f'Extension not found: loadercog')
    except Exception as e:
        print(f'Failed to load extension loadercog. Reason: {e}')

    bot.tree.add_command(group)

    print("Synced the following commands:\n", await bot.tree.sync(guild=bot.currentGuild))
    print("Connected to the Guild!")

# @bot.tree.command(name="test",description="Redesigned")
# # @app_commands.describe(member='The member to select', channel='The text-channel to select')
# async def preview_command(interaction: discord.Interaction):
#     embed = {
#         "title": "Test Embed",
#         "type": "rich",
#         "color": 0x0000ee
#     }
#     await interaction.response.send_message(f"Test command ran",embed=discord.Embed.from_dict(embed))
#     interaction.

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.followup.send(f'Slow down! Try again in {error.retry_after:.2f} seconds...', ephemeral=True)
    else:
        print(error)
        await interaction.followup.send(f'ERROR: {error}', ephemeral=True)


bot.run(TOKEN)