from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
import requests
import html
from cogs.helper import handleResponse, BearerAuth
from glot import Glot


class GlanvasConfigCog(commands.Cog):

    def __init__(self, bot: Glot) -> None:
        self.bot: Glot = bot
        self.URL = lambda: self.bot.glanvasURL + 'config/'

    async def cog_load(self):
        glanvasGroup = self.bot.tree.get_command('glanvas', guild=self.bot.currentGuild)
        if isinstance(glanvasGroup, app_commands.Group):
            group = app_commands.Group(name='config', description='Make changes to the settings on the Glanvas')
            group2 = app_commands.Group(name='url', description='Make changes to the Glanvas URL stored in The Glot')

            @group.command(name="get", description="Lists a configuration setting")
            @app_commands.describe(name='The name of the setting or `all`')
            async def get_config(interaction: discord.Interaction, name: Literal['all', 'pageBase', 'username', 'password', 'web-user', 'web-pass']):
                await interaction.response.defer(thinking=True)
                if (name == ''):
                    await interaction.followup.send('ERROR: `name` cannot be empty')
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
                await interaction.followup.send(result)



            @group.command(name="set", description="Sets a configuration setting")
            @app_commands.describe(name='The name of the setting', value='The new value for that setting')
            async def set_config(interaction: discord.Interaction, name: Literal['pageBase', 'username', 'password', 'web-user', 'web-pass'], value:str):
                await interaction.response.defer(thinking=True)
                if (name == ''):
                    await interaction.followup.send('ERROR: `name` cannot be empty')
                    return
                if (value == ''):
                    await interaction.followup.send('ERROR: `value` cannot be empty')
                    return
                
                response = requests.post(self.URL() + name, data=value, auth=BearerAuth())
                result = handleResponse(response, f'Successfully set configuration `{name}` to `{value}`')
                await interaction.followup.send(result)

            @group.command(name="reset", description="Resets a configuration setting to default")
            @app_commands.describe(name='The name of the setting')
            async def reset_config(interaction: discord.Interaction, name: Literal['pageBase', 'username', 'password', 'web-user', 'web-pass']):
                await interaction.response.defer(thinking=True)
                if (name == ''):
                    await interaction.followup.send('ERROR: `name` cannot be empty')
                    return

                response = requests.delete(self.URL() + name, auth=BearerAuth())
                result = handleResponse(response, f'Successfully reset configuration `{name}`')
                await interaction.followup.send(result)
            
            async def force_logout(interaction: discord.Interaction):
                await interaction.response.defer(thinking=True)
                response = requests.post(self.bot.glanvasURL + 'force-logout', auth=BearerAuth())
                result = handleResponse(response, 'Successfully logged out all users')
                await interaction.followup.send(result)

            logout_command = app_commands.Command(
                name="force-logout",
                callback= force_logout,
                guild_ids=[self.bot.currentGuild.id],
                description="Forcefully logs out all users. Only use when necessary"
            )

            @group2.command(name="get", description="Gets the current Glanvas URL stored in The Glot")
            async def get_url(interaction: discord.Interaction):
                await interaction.response.defer(thinking=True)
                await interaction.followup.send(f'`{self.bot.glanvasURL}`')

            @group2.command(name="set", description="Sets the current Glanvas URL stored in The Glot")
            @app_commands.describe(url='The new URL where the Glanvas is hosted')
            async def get_url(interaction: discord.Interaction, url: str):
                await interaction.response.defer(thinking=True)
                if (url == ''):
                    await interaction.followup.send('ERROR: `url` cannot be empty')
                    return
                temp = self.bot.glanvasURL
                self.bot.glanvasURL = url
                await interaction.followup.send(f'Successfully changed URL from `{temp}` to `{url}`')

            @group2.command(name="reset", description="Resets the Glanvas URL stored in The Glot to default")
            async def get_url(interaction: discord.Interaction):
                await interaction.response.defer(thinking=True)
                temp = self.bot.glanvasURL
                self.bot.glanvasURL = self.bot.defaultURL
                await interaction.followup.send(f'Successfully changed URL from `{temp}` to `{self.bot.defaultURL}`')

            glanvasGroup.add_command(group)
            glanvasGroup.add_command(group2)
            glanvasGroup.add_command(logout_command)

async def setup(bot: Glot):
    await bot.add_cog(GlanvasConfigCog(bot), guild=bot.currentGuild)