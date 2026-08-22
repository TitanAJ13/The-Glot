from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
import requests
import html
from cogs.helper import handleResponse, BearerAuth
from glot import Glot


class GlanvasCog(commands.Cog):
    group = app_commands.Group(name='glanvasconfig', description='Make changes to the settings on the Glanvas')

    def __init__(self, bot: Glot, base) -> None:
        self.bot: Glot = bot
        self.URL: str = base + 'config/'
        self.group._guild_ids = [bot.currentGuild.id]


    @group.command(name="get", description="Lists a configuration setting")
    @app_commands.describe(name='The name of the setting or `all`')
    async def get_config(self, interaction: discord.Interaction, name: Literal['all', 'authorization', 'pageBase', 'username', 'password', 'web-user', 'web-pass']):
        if (name == ''):
            await interaction.response.send_message('ERROR: `name` cannot be empty')
            return

        result = ''
        try:
            response = requests.get(self.URL + name, auth=BearerAuth())
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
    async def set_config(self, interaction: discord.Interaction, name: Literal['authorization', 'pageBase', 'username', 'password', 'web-user', 'web-pass'], value:str):
        if (name == ''):
            await interaction.response.send_message('ERROR: `name` cannot be empty')
            return
        if (value == ''):
            await interaction.response.send_message('ERROR: `value` cannot be empty')
            return
        
        response = requests.post(self.URL + name, data=value, auth=BearerAuth())
        result = handleResponse(response, f'Successfully set configuration `{name}` to `{value}`')
        await interaction.response.send_message(result)

    @group.command(name="reset", description="Resets a configuration setting to default")
    @app_commands.describe(name='The name of the setting')
    async def reset_config(self, interaction: discord.Interaction, name: Literal['authorization', 'pageBase', 'username', 'password', 'web-user', 'web-pass']):
        if (name == ''):
            await interaction.response.send_message('ERROR: `name` cannot be empty')
            return

        response = requests.delete(self.URL + name, auth=BearerAuth())
        result = handleResponse(response, 'Successfully reset configuration `{name}`')
        await interaction.response.send_message(result)

async def setup(bot: Glot):
    await bot.add_cog(GlanvasCog(bot, bot.glanvasURL), guild=bot.currentGuild)