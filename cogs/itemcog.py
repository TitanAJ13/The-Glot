from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
import requests

class ItemCog(commands.Cog):
    def __init__(self, bot: commands.Bot, base) -> None:
        self.bot = bot
        self.URL = base + 'items/'

    group = app_commands.Group(name='item', description='Make changes to the module subitems on the Glanvas', guild_ids=[1378895395253387344])

    @group.command(name="add", description="Adds a new item to a module")
    @app_commands.describe(moduleposition="The position of the item's container module", title='Item display title', type='The type of item to add', url='The url for the item. Leave blank if making a header', hidden='Optional: If the item should be hidden from view', position='Optional: The position to insert it into')
    async def add_item(self, interaction: discord.Interaction, moduleposition: int, title: str, type: Literal['internal', 'external', 'file', 'music', 'page','form','header'], url: str, hidden: Optional[Literal['True', 'False']] = 'False', position: Optional[int] = None):
        title = title.strip()
        url = url.strip()
        if (moduleposition < 1):
            await interaction.response.send_message('ERROR: `moduleposition` cannot be less than 1')
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
        if (position is not None and position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1 if defined')
            return
        
        itemObj = {
            'moduleposition': moduleposition,
            'display': title,
            'type': type,
            'url': url,
            'position': position,
            'hidden': bool(hidden)
        }
        
        response = requests.post(self.URL, json=itemObj).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully created the module item')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="remove", description="Removes an existing module item")
    @app_commands.describe(moduleposition='The position of the module in the list', position='The position of the item within the module')
    async def remove_item(self, interaction: discord.Interaction, moduleposition: int, position: int):
        if (moduleposition < 1):
            await interaction.response.send_message('ERROR: `moduleposition` cannot be less than 1')
            return
        if (position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1')
            return
        
        response = requests.delete(self.URL, json={'moduleposition': moduleposition, 'position': position}).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully deleted the item')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="edit", description="Edits an existing module item")
    @app_commands.describe(moduleposition='The position of the module in the list', position='The position of the item to edit within the module', title='Item display title', type='The type of item', url='The url for the item. Leave blank if making a header')
    async def edit_item(self, interaction: discord.Interaction, moduleposition: int, position: int, title: Optional[str] = None, type: Optional[Literal['internal', 'external', 'file', 'music', 'page','form','header']] = None, url: Optional[str] = None):
        if (moduleposition < 1):
            await interaction.response.send_message('ERROR: `moduleposition` cannot be less than 1')
            return
        if (position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1')
            return
        if (type is None and title is None and url is None):
            await interaction.response.send_message('ERROR: at least one of `type`, `title`, or `url` must be defined')
            return
        if (title is not None and title.strip() == ''):
            await interaction.response.send_message('ERROR: `title` cannot be empty if it is used')
            return
        if (url is not None and url.strip() == ''):
            await interaction.response.send_message('ERROR: `url` cannot be empty if it is used')
            return
        
        changes = {}

        if (title is not None):
            changes.display_name = title.strip()
        if (type is not None):
            changes.type = type
        if (url is not None):
            changes.url = url.strip()
        
        itemObj = {
            'moduleposition': moduleposition,
            'position': position,
            'changes': changes
        }

        response = requests.patch(self.URL, json=itemObj).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully editted the item')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="move", description="Moves a module item to a different position within the same module")
    @app_commands.describe(moduleposition='The position of the module in the list', position1='The current position of the item within the module', position2='The position for the item to end up at')
    async def move_item(self, interaction: discord.Interaction, moduleposition: int, position1: int, position2: int):
        if (moduleposition < 1):
            await interaction.response.send_message('ERROR: `moduleposition` cannot be less than 1')
            return
        if (position1 < 1):
            await interaction.response.send_message('ERROR: `position1` cannot be less than 1')
            return
        if (position2 < 1):
            await interaction.response.send_message('ERROR: `position2` cannot be less than 1')
            return
        
        itemObj = {
            'moduleposition': moduleposition,
            'position1': position1,
            'position2': position2
        }
        
        response = requests.put(self.URL, json=itemObj).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully moved the item')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="hide", description="Hides a module item from view")
    @app_commands.describe(moduleposition='The position of the module in the list', position='The position of the item within the module')
    async def hide_item(self, interaction: discord.Interaction, moduleposition: int, position: int):
        if (moduleposition < 1):
            await interaction.response.send_message('ERROR: `moduleposition` cannot be less than 1')
            return
        if (position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1')
            return
        
        itemObj = {
            'moduleposition': moduleposition,
            'position': position,
            'changes': {
                'hidden': True
            }
        }

        response = requests.patch(self.URL, json=itemObj).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully hid the item')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="show", description="Makes a hidden module item visible")
    @app_commands.describe(moduleposition='The position of the module in the list', position='The position of the item within the module')
    async def show_item(self, interaction: discord.Interaction, moduleposition: int, position: int):
        if (moduleposition < 1):
            await interaction.response.send_message('ERROR: `moduleposition` cannot be less than 1')
            return
        if (position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1')
            return
        
        itemObj = {
            'moduleposition': moduleposition,
            'position': position,
            'changes': {
                'hidden': False
            }
        }

        response = requests.patch(self.URL, json=itemObj).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully made the item visible')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

async def setup(bot: commands.Bot):
    await bot.add_cog(ItemCog(bot))