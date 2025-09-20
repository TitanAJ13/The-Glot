from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
import requests

class LinkCog(commands.Cog):
    def __init__(self, bot: commands.Bot, base) -> None:
        self.bot = bot
        self.URL = base + 'links/'

    group = app_commands.Group(name='link', description='Make changes to the links on the Glanvas', guild_ids=[1378895395253387344])

    @group.command(name="add", description="Adds a new link")
    @app_commands.describe(type='Type of link', title='Link display title', url='The actual URL', position='Optional: The position to insert it into')
    async def add_link(self, interaction: discord.Interaction, type: Literal['internal','external','file','music','page','form'], title: str, url: str, position: Optional[int] = None):
        if (position is not None and position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1')
            return
        if (title == ''):
            await interaction.response.send_message('ERROR: `title` cannot be empty')
            return
        if (url == ''):
            await interaction.response.send_message('ERROR: `url` cannot be empty')
            return
        if (type == 'internal' and url not in ['home', 'announcements', 'modules']):
            await interaction.response.send_message("ERROR: Internal URLs can only be `home`, `modules`, or `announcements`.")
            return
        if (type == 'external' and url[:8] != 'https://'):
            await interaction.response.send_message("ERROR: External URLs must start with `https://`.")
            return
        title = title.strip()
        url = url.strip()
        linkObj = {
            'display_name': title,
            'type': type,
            'url': url,
            'position': position
        }
        response = requests.post(self.URL, json=linkObj).json()
        if (response.status == 'success'):
            await interaction.response.send_message('Succesfully posted link')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')


    @group.command(name="remove", description="Removes an existing link")
    @app_commands.describe(position='The position of the link in the list')
    async def remove_link(self, interaction: discord.Interaction, position: int):
        if (position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1')
            return

        response = requests.delete(self.URL, json={'position': position}).json()
        if (response.status == 'success'):
            await interaction.response.send_message(f'Successfully removed the link at position {position}')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="edit", description="Edits an existing link")
    @app_commands.describe(position='The position of the link to edit', type='Type of link', title='Link display title', url='The actual URL')
    async def edit_link(self, interaction: discord.Interaction, position: int, type: Optional[Literal['internal','external','file','music','page','form']] = None, title: Optional[str] = None, url: Optional[str] = None):
        if (position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1')
            return
        if (type is None and title is None and url is None):
            await interaction.response.send_message('ERROR: at least one of `type`, `title`, or `url` must be defined')
            return
        if (title is not None and title == ''):
            await interaction.response.send_message('ERROR: `title` cannot be empty if it is used')
            return
        if (url is not None and url == ''):
            await interaction.response.send_message('ERROR: `url` cannot be empty if it is used')
            return
        
        changes = {}

        if (type is not None):
            changes.type = type
        if (title is not None):
            changes.title = title
        if (url is not None):
            changes.url = url

        linkObj = {
            'position': position,
            'changes': changes
        }

        response = requests.patch(self.URL, json=linkObj).json()

        if (response.status == 'success'):
            interaction.response.send_message('Successfully edited the link')
        else:
            interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="move", description="Move a link to a different position")
    @app_commands.describe(position1='The current position of the link', position2='The position to end up at')
    async def move_link(self, interaction: discord.Interaction, position1: int, position2: int):
        if (position1 < 1):
            await interaction.response.send_message('ERROR: `position1` cannot be less than 1')
            return
        if (position2 < 1):
            await interaction.response.send_message('ERROR: `position2` cannot be less than 1')
            return
        
        response = requests.put(self.URL, json={'position1': position1, 'position2': position2}).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully moved the link')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

async def setup(bot: commands.Bot):
    await bot.add_cog(LinkCog(bot))