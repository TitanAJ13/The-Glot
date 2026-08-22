from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
import requests
import html
from cogs.helper import handleResponse, BearerAuth
from glot import Glot


class GlanvasCog(commands.Cog):
    group = app_commands.Group(name='glanvas', description='Make changes to the settings on the Glanvas')

    def __init__(self, bot: Glot) -> None:
        self.bot: Glot = bot
        self.URL = lambda: self.bot.glanvasURL + 'config/'
        self.group._guild_ids = [bot.currentGuild.id]


    @group.command(name="get", description="Lists a configuration setting")
    @app_commands.describe(name='The name of the setting or `all`')
    async def get_config(self, interaction: discord.Interaction, name: Literal['all', 'pageBase', 'username', 'password', 'web-user', 'web-pass']):
        if (name == ''):
            await interaction.response.send_message('ERROR: `name` cannot be empty')
            return

        result = ''
        try:
            response = requests.get(self.URL() + name, auth=BearerAuth())
            response.raise_for_status()
            if (name == 'all'):
                json = response.json()
                del json['authorization']
                del json['calendarDelta']
                del json['calendarNum']
                del json['homeAnnouncements']
                result = 'Settings:'
                for key in json.keys():
                    result = result + f'\n* `{key}`: `{json[key]}`'
            else:
                result = f'`{name}`: `{response.text}`'
        except requests.HTTPError as e:
            result = "ERROR: " + html.unescape(e.response.text.split("<p>")[1].split("</p>")[0])
        except Exception as e:
            result = f"ERROR: {e}"
        await interaction.response.send_message(result)



    @group.command(name="set", description="Sets a configuration setting")
    @app_commands.describe(name='The name of the setting', value='The new value for that setting')
    async def set_config(self, interaction: discord.Interaction, name: Literal['pageBase', 'username', 'password', 'web-user', 'web-pass'], value:str):
        if (name == ''):
            await interaction.response.send_message('ERROR: `name` cannot be empty')
            return
        if (value == ''):
            await interaction.response.send_message('ERROR: `value` cannot be empty')
            return
        
        response = requests.post(self.URL() + name, data=value, auth=BearerAuth())
        result = handleResponse(response, f'Successfully set configuration `{name}` to `{value}`')
        await interaction.response.send_message(result)

    @group.command(name="reset", description="Resets a configuration setting to default")
    @app_commands.describe(name='The name of the setting')
    async def reset_config(self, interaction: discord.Interaction, name: Literal['pageBase', 'username', 'password', 'web-user', 'web-pass']):
        if (name == ''):
            await interaction.response.send_message('ERROR: `name` cannot be empty')
            return

        response = requests.delete(self.URL() + name, auth=BearerAuth())
        result = handleResponse(response, f'Successfully reset configuration `{name}`')
        await interaction.response.send_message(result)

    @group.command(name="force-logout", description="Forcefully logs out all users. Only use when necessary")
    async def force_logout(self, interaction: discord.Interaction):
        response = requests.post(self.bot.glanvasURL + 'force-logout', auth=BearerAuth())
        result = handleResponse(response, 'Successfully logged out all users')
        await interaction.response.send_message(result)

    @group.command(name="url-get", description="Gets the current Glanvas URL stored in The Glot")
    async def get_url(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'`{self.bot.glanvasURL}`')

    @group.command(name="url-set", description="Sets the current Glanvas URL stored in The Glot")
    @app_commands.describe(url='The new URL where the Glanvas is hosted')
    async def get_url(self, interaction: discord.Interaction, url: str):
        if (url == ''):
            await interaction.response.send_message('ERROR: `url` cannot be empty')
            return
        temp = self.bot.glanvasURL
        self.bot.glanvasURL = url
        await interaction.response.send_message(f'Successfully changed URL from `{temp}` to `{url}`')

    @group.command(name="url-reset", description="Resets the Glanvas URL stored in The Glot to default")
    async def get_url(self, interaction: discord.Interaction):
        temp = self.bot.glanvasURL
        self.bot.glanvasURL = self.bot.defaultURL
        await interaction.response.send_message(f'Successfully changed URL from `{temp}` to `{self.bot.defaultURL}`')

async def setup(bot: Glot):
    await bot.add_cog(GlanvasCog(bot), guild=bot.currentGuild)