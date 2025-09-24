from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
import requests

class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot, base) -> None:
        self.bot = bot
        self.URL = base + 'musicdata/'

    group = app_commands.Group(name='music', description='Make changes to the registered sheetmusic on the Glanvas', guild_ids=[1378895395253387344])

    @group.command(name="add", description="Registers new sheetmusic")
    @app_commands.describe(url='Link to the sheetmusic', filename='What to call the sheetmusic', path='The special glanvas url to give to this sheetmusic')
    async def add_music(self, interaction: discord.Interaction, url: str, filename: str, path: str):
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

        musicObj = {
            'key': path,
            'url': url,
            'display_name': filename
        }

        response = requests.post(self.URL, json=musicObj).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully registered the sheetmusic')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="remove", description="Removes registered sheetmusic")
    @app_commands.describe(path='The special glanvas url to remove')
    async def remove_music(self, interaction: discord.Interaction, path: str):
        if (path == ''):
            await interaction.response.send_message('ERROR: `path` cannot be empty')
            return

        response = requests.delete(self.URL, json={'key': path}).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully removed the registered sheetmusic')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="edit", description="Edits an existing sheetmusic registration")
    @app_commands.describe(path ='The special glanvas url for the sheetmusic', new_path = "The updated special glanvas url", url='The url for the sheetmusic', filename='What to call the sheetmusic' )
    async def edit_music(self, interaction: discord.Interaction, path: str, new_path: Optional[str] = None, filename: Optional[str] = None, url: Optional[str] = None):
        path = path.strip()
        if (path == ''):
            await interaction.response.send_message('ERROR: `path` cannot be empty')
            return
        if (new_path is None and filename is None and url is None):
            await interaction.response.send_message('ERROR: at least one of `new_path`, `filename`, or `url` must be defined')
            return
        if (new_path is not None and new_path.strip() == ''):
            await interaction.response.send_message('ERROR: `new_path` cannot be empty if it is used')
            return
        if (filename is not None and filename.strip() == ''):
            await interaction.response.send_message('ERROR: `filename` cannot be empty if it is used')
            return
        if (url is not None and url.strip() == ''):
            await interaction.response.send_message('ERROR: `url` cannot be empty if it is used')
            return
        
        changes = {}

        if (new_path is not None):
            changes.path = new_path.strip()
        if (filename is not None):
            changes.display_name = filename.strip()
        if (url is not None):
            changes.url = url.strip()

        musicObj = {
            'key': path,
            'changes': changes
        }

        response = requests.patch(self.URL, json=musicObj).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully edited the registered sheetmusic')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

async def setup(bot: commands.Bot):
    await bot.add_cog(MusicCog(bot))