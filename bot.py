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

# @client.event
@bot.event
async def on_ready():
    # global data
    # try:
    #     data = pd.read_excel("H:/My Drive/The Google Glive/Fall 2025 Roster.xlsx",sheet_name="Roster", usecols=[0,1,2,4,6,7,13], index_col=2)
    #     data.index = data.index.str.lower()
    # except Exception as e:
    #     print(f'Roster could not be loaded: {e}')

    
    guildPMGC = bot.get_guild(614104404102086658)
    guildTest = bot.get_guild(1378895395253387344)

    bot.tree.clear_commands(guild=None)

    bot.glanvasURL = 'https://pmgc.pythonanywhere.com/'
    bot.setGuild(guildPMGC)
    bot.roster_id = "1bL1uw6ohQ9HNASGVA46ve6_koTpJ6htSBPrwwyWq-TQ"

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

    await bot.load_extension("loadercog")

    print("Synced the following commands:\n", await bot.tree.sync(guild=bot.currentGuild))
    print("Connected to the Guild!")

# @bot.tree.context_menu(name="Test Menu")
# @app_commands.guilds(1378895395253387344)
# async def react(interaction: discord.Interaction, message: discord.Message):
#     await interaction.response.send_message('Very cool message!', ephemeral=True)

# Command to sync application commands
@bot.command(name='sync')
@commands.is_owner() # Optional: Restrict to bot owner
async def sync(ctx):
    globalResults = await bot.tree.sync(guild=None)
    guildResults = await bot.tree.sync(guild=bot.currentGuild)
    await ctx.send(f"Synced the following global commands: {globalResults}\nSynced the following guild commands: {guildResults}")

# Command to sync application commands
@bot.command(name='clear')
@commands.is_owner() # Optional: Restrict to bot owner
async def clear(ctx):
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync(guild=None)
    await ctx.send(f"Cleared commands")


''' Command syntax:

/glanvas link|module|announcement all|

/glanvas add|delete|clear link|module -> UI

/glanvas add link|module -> UI
/glanvas delete link|module|announcement?
/
'''

# bot.create

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



bot.run(TOKEN)