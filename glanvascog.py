from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
import requests
import html
from cogs.helper import handleResponse, BearerAuth
from glot import Glot


class GlanvasCog(commands.Cog):

    def __init__(self, bot: Glot) -> None:
        self.bot: Glot = bot
        self.glanvasgroup = app_commands.Group(name='glanvas', description='Make changes to the Glanvas')
        self.glanvasgroup._guild_ids = [bot.currentGuild.id]
        self.bot.tree.add_command(self.glanvasgroup)

async def setup(bot: Glot):
    await bot.add_cog(GlanvasCog(bot), guild=bot.currentGuild)