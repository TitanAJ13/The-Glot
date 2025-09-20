from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
import requests

class ModuleCog(commands.Cog):
    def __init__(self, bot: commands.Bot, base) -> None:
        self.bot = bot
        self.URL = base + 'modules/'

    group = app_commands.Group(name='module', description='Make changes to the modules on the Glanvas', guild_ids=[1378895395253387344])

    @group.command(name="add", description="Adds a new module")
    @app_commands.describe(title='Module display title', hidden='Optional: If the module should be hidden from view', position='Optional: The position to insert it into')
    async def add_module(self, interaction: discord.Interaction, title: str, hidden: Optional[Literal['True', 'False']] = 'False', position: Optional[int] = None):
        if (title == ''):
            await interaction.response.send_message('ERROR: `title` cannot be empty')
            return
        if (position is not None and position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1 if defined')
            return
        
        moduleObj ={
            'display_name': title,
            'position': position,
            'hidden': bool(hidden)
        }

        response = requests.post(self.URL, json=moduleObj).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully added the new module')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="remove", description="Removes an existing module and all items within it")
    @app_commands.describe(position='The position of the module in the list')
    async def remove_module(self, interaction: discord.Interaction, position: int):
        if (position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1')
            return
        
        response = requests.delete(self.URL, json={'position': position}).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully deleted the module')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="edit", description="Edits an existing module")
    @app_commands.describe(position='The position of the module to edit', title='Module display title')
    async def edit_module(self, interaction: discord.Interaction, position: int, title: str):
        if (position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1')
            return
        if (title == ''):
            await interaction.response.send_message('ERROR: `title` cannot be empty')
            return
        
        moduleObj = {
            'position': position,
            'changes': {
                'display_name': title
            }
        }

        response = requests.patch(self.URL, json=moduleObj).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully editted the module')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="move", description="Moves a module to a different position")
    @app_commands.describe(position1='The current position of the module', position2='The position to end up at')
    async def move_module(self, interaction: discord.Interaction, position1: int, position2: int):
        if (position1 < 1):
            await interaction.response.send_message('ERROR: `position1` cannot be less than 1')
            return
        if (position2 < 1):
            await interaction.response.send_message('ERROR: `position2` cannot be less than 1')
            return
        
        response = requests.put(self.URL, json={'position1': position1, 'position2': position2}).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully moved the module')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="hide", description="Hides a module from view")
    @app_commands.describe(position='The position of the module')
    async def hide_module(self, interaction: discord.Interaction, position: int):
        if (position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1')
            return
        
        moduleObj = {
            'position': position,
            'changes': {
                'hidden': True
            }
        }

        response = requests.patch(self.URL, json=moduleObj).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully hid the module')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

    @group.command(name="show", description="Makes a hidden module visible")
    @app_commands.describe(position='The position of the module')
    async def show_module(self, interaction: discord.Interaction, position: int):
        if (position < 1):
            await interaction.response.send_message('ERROR: `position` cannot be less than 1')
            return
        
        moduleObj = {
            'position': position,
            'changes': {
                'hidden': False
            }
        }

        response = requests.patch(self.URL, json=moduleObj).json()

        if (response.status == 'success'):
            await interaction.response.send_message('Successfully made the module visible')
        else:
            await interaction.response.send_message(f'ERROR: {response.message}')

async def setup(bot: commands.Bot):
    await bot.add_cog(ModuleCog(bot))