from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
import requests
from cogs.helper import handleResponse, BearerAuth
from glot import Glot

class FileCog(commands.Cog):

    def __init__(self, bot: Glot) -> None:
        self.bot: Glot = bot
        self.URL = lambda: self.bot.glanvasURL + 'files/'

    async def cog_load(self):
        glanvasGroup = self.bot.tree.get_command('glanvas', guild=self.bot.currentGuild)
        if isinstance(glanvasGroup, app_commands.Group):
            group = app_commands.Group(name='file', description='Make changes to the registered files on the Glanvas')

            @group.command(name="add", description="Registers a new file")
            @app_commands.describe(url='Link to the file', filename='What to call the file', path='The special glanvas url to give to this file')
            async def add_file(interaction: discord.Interaction, url: str, filename: str, path: str):
                await interaction.response.defer(thinking=True)
                url = url.strip()
                filename = filename.strip()
                path = path.strip()
                if (url == ''):
                    await interaction.followup.send('ERROR: `url` cannot be empty.')
                    return
                if (filename == ''):
                    await interaction.followup.send('ERROR: `filename` cannot be empty.')
                    return
                if (path == ''):
                    await interaction.followup.send('ERROR: `path` cannot be empty.')
                    return
                if (url[:8] != 'https://'):
                    await interaction.followup.send('ERROR: `url` must start with `https://`.')

                # make sure url is a preview URL
                arr = url.split('/')
                arr[-1] = 'preview'
                url = '/'.join(arr)

                fileObj = {
                    'key': path,
                    'url': url,
                    'display_name': filename
                }

                response = requests.post(self.URL(), json=fileObj, auth=BearerAuth())
                result = handleResponse(response, 'Successfully registered the file')
                await interaction.followup.send(result)

            @group.command(name="remove", description="Removes a registered file")
            @app_commands.describe(path='The special glanvas url to remove')
            async def remove_file(interaction: discord.Interaction, path: str):
                await interaction.response.defer(thinking=True)
                if (path == ''):
                    await interaction.followup.send('ERROR: `path` cannot be empty')
                    return

                response = requests.delete(self.URL(), json={'key': path}, auth=BearerAuth())
                result = handleResponse(response, 'Successfully removed the registered file')
                await interaction.followup.send(result)

            @group.command(name="edit", description="Edits an existing file registration")
            @app_commands.describe(path ='The special glanvas url for the file', new_path = "The updated special glanvas url", url='The url for the file', filename='What to call the file' )
            async def edit_file(interaction: discord.Interaction, path: str, new_path: Optional[str] = None, filename: Optional[str] = None, url: Optional[str] = None):
                await interaction.response.defer(thinking=True)
                if (path == ''):
                    await interaction.followup.send('ERROR: `path` cannot be empty')
                    return
                if (new_path is None and filename is None and url is None):
                    await interaction.followup.send('ERROR: at least one of `new_path`, `filename`, or `url` must be defined')
                    return
                if (new_path is not None and new_path == ''):
                    await interaction.followup.send('ERROR: `new_path` cannot be empty if it is used')
                    return
                if (filename is not None and filename == ''):
                    await interaction.followup.send('ERROR: `filename` cannot be empty if it is used')
                    return
                if (url is not None and url == ''):
                    await interaction.followup.send('ERROR: `url` cannot be empty if it is used')
                    return
                
                # make sure url is a preview URL
                if (url is not None):
                    arr = url.split('/')
                    arr[-1] = 'preview'
                    url = '/'.join(arr)
                
                changes = {}

                if (new_path is not None):
                    changes['path'] = new_path
                if (filename is not None):
                    changes['display_name'] = filename
                if (url is not None):
                    changes['url'] = url

                fileObj = {
                    'key': path,
                    'changes': changes
                }

                response = requests.patch(self.URL(), json=fileObj, auth=BearerAuth())
                result = handleResponse(response, 'Successfully edited the registered file')
                await interaction.followup.send(result)

            glanvasGroup.add_command(group)
        

async def setup(bot: Glot):
    await bot.add_cog(FileCog(bot), guild=bot.currentGuild)