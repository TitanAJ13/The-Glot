from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
import requests

def handleResponse(response: requests.Response, success: str) -> str:
    try:
        response.raise_for_status()
        json = response.json()
        if (json['status'] == 'success'):
            return success
        else:
            return "Something went wrong..."
    except Exception as e:
        return f"ERROR: {e}"

class FileCog(commands.Cog):
    def __init__(self, bot: commands.Bot, base) -> None:
        self.bot = bot
        self.URL = base + 'files/'

    group = app_commands.Group(name='file', description='Make changes to the registered files on the Glanvas', guild_ids=[1378895395253387344])

    @group.command(name="add", description="Registers a new file")
    @app_commands.describe(url='Link to the file', filename='What to call the file', path='The special glanvas url to give to this file')
    async def add_file(self, interaction: discord.Interaction, url: str, filename: str, path: str):
        url = url.strip()
        filename = filename.strip()
        path = path.strip()
        if (url == ''):
            await interaction.response.send_message('ERROR: `url` cannot be empty.')
            return
        if (filename == ''):
            await interaction.response.send_message('ERROR: `filename` cannot be empty.')
            return
        if (path == ''):
            await interaction.response.send_message('ERROR: `path` cannot be empty.')
            return
        if (url[:8] != 'https://'):
            await interaction.response.send_message('ERROR: `url` must start with `https://`.')

        # make sure url is a preview URL
        arr = url.split('/')
        arr[-1] = 'preview'
        url = '/'.join(arr)

        fileObj = {
            'key': path,
            'url': url,
            'display_name': filename
        }

        response = requests.post(self.URL, json=fileObj)
        result = handleResponse(response, 'Successfully registered the file')
        await interaction.response.send_message(result)

    @group.command(name="remove", description="Removes a registered file")
    @app_commands.describe(path='The special glanvas url to remove')
    async def remove_file(self, interaction: discord.Interaction, path: str):
        if (path == ''):
            await interaction.response.send_message('ERROR: `path` cannot be empty')
            return

        response = requests.delete(self.URL, json={'key': path})
        result = handleResponse(response, 'Successfully removed the registered file')
        await interaction.response.send_message(result)

    @group.command(name="edit", description="Edits an existing file registration")
    @app_commands.describe(path ='The special glanvas url for the file', new_path = "The updated special glanvas url", url='The url for the file', filename='What to call the file' )
    async def edit_file(self, interaction: discord.Interaction, path: str, new_path: Optional[str] = None, filename: Optional[str] = None, url: Optional[str] = None):
        if (path == ''):
            await interaction.response.send_message('ERROR: `path` cannot be empty')
            return
        if (new_path is None and filename is None and url is None):
            await interaction.response.send_message('ERROR: at least one of `new_path`, `filename`, or `url` must be defined')
            return
        if (new_path is not None and new_path == ''):
            await interaction.response.send_message('ERROR: `new_path` cannot be empty if it is used')
            return
        if (filename is not None and filename == ''):
            await interaction.response.send_message('ERROR: `filename` cannot be empty if it is used')
            return
        if (url is not None and url == ''):
            await interaction.response.send_message('ERROR: `url` cannot be empty if it is used')
            return
        
        changes = {}

        if (new_path is not None):
            changes.path = new_path
        if (filename is not None):
            changes.display_name = filename
        if (url is not None):
            changes.url = url

        fileObj = {
            'key': path,
            'changes': changes
        }

        response = requests.patch(self.URL, json=fileObj)
        result = handleResponse(response, 'Successfully edited the registered file')
        await interaction.response.send_message(result)
        

async def setup(bot: commands.Bot):
    await bot.add_cog(FileCog(bot))