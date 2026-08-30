from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
from glot import Glot


class ConfigCog(commands.Cog):
    config = app_commands.Group(name='config', description="Make changes to The Glot's settings")
    rolegroup = app_commands.Group(name='roles', description="Make changes to the stored role information", parent=config)
    columngroup = app_commands.Group(name='column', description="Make changes to the stored column information", parent=config)
    sheetgroup = app_commands.Group(name='sheet', description="Make changes to the stored sheet information", parent=config)
    ids = app_commands.Group(name='ids', description="Make changes to the stored ID information", parent=config)

    def __init__(self, bot: Glot) -> None:
        self.bot: Glot = bot
        self.roleConversion = {
            'Verified User': 'check',
            'Tenor 1': 't1',
            'Tenor 2': 't2',
            'Baritone': 'bari',
            'Bass': 'bass',
            'Tacet': 'tacet',
            'Pantherhythms': 'panther',
            'Tour': 'tour',
            'Alumni': 'alumni'
        }
        self.columnConversion = {
            'Last Name': 'lastName',
            'First Name': 'firstName',
            'Preferred Name': 'preferredName',
            'Concert Name': 'concertName',
            'Nickname': 'nickname',
            'School Email': 'schoolEmail',
            'Personal Email': 'personalEmail',
            'Phone Number': 'phone',
            'Voice Part': 'voicePart',
            'Voice Split': 'voiceSplit',
            'Tacet': 'tacet',
            'Grade Level': 'gradeLevel',
            'Grad Year': 'gradYear',
            'Newbie': 'newbie',
            'Pantherhythms': 'pantherhythms',
            'Tour': 'tour',
            'Shirt Size': 'shirt',
            'Student ID': 'studentId',
            'Discord ID': 'discordId'
        }
        self.sheetConversion = {
            'Full Roster': 'fullRoster',
            'Current Roster': 'currentRoster'
        }
        self.idConversion = {
            'Calendar': 'calendarID',
            'Roster': 'roster_id'
        }

    @ids.command(name="list", description='Lists all stored ID information')
    async def list_ids(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        result = "These are the IDs stored in The Glot:"

        result = result + f'\n* Google Calendar: `{self.bot.calendarId}`'
        result = result + f'\n* Working Roster: `{self.bot.roster_id}`'

        await interaction.followup.send(result)

    @ids.command(name="set", description='Sets a stored ID')
    @app_commands.describe(name='The name of the ID to modify', value='The new ID')
    async def set_id(self, interaction: discord.Interaction, name: Literal['Calendar', 'Roster'], value: str):
        await interaction.response.defer(thinking=True)
        if (name == ''):
            await interaction.followup.send('ERROR: `name` cannot be empty')
            return
        if (value == ''):
            await interaction.followup.send('ERROR: `value` cannot be empty')
            return

        temp = getattr(self.bot, self.idConversion[name])
        
        setattr(self.bot, self.idConversion[name], value.name)

        result = f'Changed {name} ID from `{temp}` to `{getattr(self.bot, self.idConversion[name])}`'
        
        await interaction.followup.send(result)

    @ids.command(name="reset", description='Resets a stored ID to default')
    @app_commands.describe(name='The name of the ID to reset')
    async def reset_id(self, interaction: discord.Interaction, name: Literal['Calendar', 'Roster']):
        await interaction.response.defer(thinking=True)
        if (name == ''):
            await interaction.followup.send('ERROR: `name` cannot be empty')
            return

        default = name
        if (default == 'Calendar'): default = self.bot.defaultCalId
        if (default == 'Roster'): default = self.bot.default_roster_id

        temp = getattr(self.bot, self.idConversion[name])
        
        setattr(self.bot, self.idConversion[name], default)

        result = f'Changed {name} ID from `{temp}` to `{getattr(self.bot, self.idConversion[name])}`'
        
        await interaction.followup.send(result)

    @rolegroup.command(name="list", description="Lists all stored role information")
    async def list_roles(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        result = "These are the Role names used in Verifications and Role Updates:"

        for key, value in self.roleConversion.items():
            result = result + f"\n* {key} Role: `{getattr(self.bot, value)}`"
        
        result = result + '\n\n**IMPORTANT: Each role should have a unique name to prevent issues with distinguishing between two roles**'
        
        await interaction.followup.send(result)

    @rolegroup.command(name="set", description="Sets a name for a stored role")
    @app_commands.describe(name='The name/purpose of the role', value='The new name to store')
    async def set_role(self, interaction: discord.Interaction, name: Literal['Verified User', 'Tenor 1', 'Tenor 2', 'Baritone', 'Bass', 'Tacet', 'Pantherhythms', 'Tour', 'Alumni'], value: discord.Role):
        await interaction.response.defer(thinking=True)
        if (name == ''):
            await interaction.followup.send('ERROR: `name` cannot be empty')
            return
        if (value == ''):
            await interaction.followup.send('ERROR: `value` cannot be empty')
            return

        temp = getattr(self.bot, self.roleConversion[name])
        
        setattr(self.bot, self.roleConversion[name], value.name)

        result = f'Changed name for {name} Role from `{temp}` to `{getattr(self.bot, self.roleConversion[name])}`'
        
        await interaction.followup.send(result)

    @rolegroup.command(name="reset", description="Resets a name for a stored role")
    @app_commands.describe(name='The name/purpose of the role')
    async def reset_role(self, interaction: discord.Interaction, name: Literal['Verified User', 'Tenor 1', 'Tenor 2', 'Baritone', 'Bass', 'Tacet', 'Pantherhythms', 'Tour', 'Alumni']):
        await interaction.response.defer(thinking=True)
        if (name == ''):
            await interaction.followup.send('ERROR: `name` cannot be empty')
            return

        default = name
        if (default == 'Verified User'): default = 'Nice Boi'
        if (default == 'Tacet'): default = 'TACET'

        temp = getattr(self.bot, self.roleConversion[name])

        setattr(self.bot, self.roleConversion[name], default)

        result = f'Changed name for {name} Role from `{temp}` to `{getattr(self.bot, self.roleConversion[name])}`'

        await interaction.followup.send(result)

    @columngroup.command(name="list", description="Lists all stored Roster column header information")
    @app_commands.describe(filter='How to filter the results')
    async def list_columns(self, interaction: discord.Interaction, filter: Literal['all', 'default', 'extra']):
        await interaction.response.defer(thinking=True)

        result = ''
        if (filter in ['all', 'default']):
            result = result + "These are the default Column Header names stored in The Glot:"

            for key, value in self.columnConversion.items():
                result = result + f"\n* {key} Column: `{getattr(self.bot.rosterColumns, value)}`"

        if (filter in ['all', 'extra']):
            if self.bot.rosterColumns.others and len(self.bot.rosterColumns.others) > 0:
                result = result + '\n\nThese are the Extra Column Header names stored in The Glot:'
                for key, value in self.bot.rosterColumns.others.items():
                    result = result + f'\n* {key} Column: `{value}`'
            else:
                result = result + '\n\nThere are no Extra Column Header names stored in The Glot'
        
        result = result + '\n\n**IMPORTANT: Each column header should have a unique name to prevent issues with distinguishing between two columns**'
        
        await interaction.followup.send(result)

    @columngroup.command(name="set", description="Sets a name for a default stored column header")
    @app_commands.describe(name='The name/purpose of the column header', value='The new name to store')
    async def set_column(self, interaction: discord.Interaction, name: Literal['Last Name', 'First Name', 'Preferred Name', 'Concert Name', 'Nickname', 'School Email', 'Personal Email', 'Phone Number', 'Voice Part', 'Voice Split', 'Tacet', 'Grade Level', 'Newbie', 'Pantherhythms', 'Tour', 'Shirt Size', 'Student ID', 'Discord ID'], value: str):
        await interaction.response.defer(thinking=True)
        if (name == ''):
            await interaction.followup.send('ERROR: `name` cannot be empty')
            return
        if (value == ''):
            await interaction.followup.send('ERROR: `value` cannot be empty')
            return

        temp = getattr(self.bot.rosterColumns, self.columnConversion[name])
        
        setattr(self.bot.rosterColumns, self.columnConversion[name], value.name)

        result = f'Changed name for {name} Column from `{temp}` to `{getattr(self.bot.rosterColumns, self.columnConversion[name])}`'

        await interaction.followup.send(result)

    @columngroup.command(name="reset", description="Resets the name for a default stored column header to default")
    @app_commands.describe(name='The name/purpose of the column header')
    async def reset_column(self, interaction: discord.Interaction, name: Literal['Last Name', 'First Name', 'Preferred Name', 'Concert Name', 'Nickname', 'School Email', 'Personal Email', 'Phone Number', 'Voice Part', 'Voice Split', 'Tacet', 'Grade Level', 'Newbie', 'Pantherhythms', 'Tour', 'Shirt Size', 'Student ID', 'Discord ID']):
        await interaction.response.defer(thinking=True)
        if (name == ''):
            await interaction.followup.send('ERROR: `name` cannot be empty')
            return

        default = name
        if (default == 'Nickname'): default = 'Glickname'
        if (default == 'School Email'): default = 'Pitt Email'
        if (default == 'Phone Number'): default = 'Phone'
        if (default == 'Voice Split'): default = 'Split'
        if (default == 'Grade Level'): default = 'Year'
        if (default == 'Student ID'): default = 'PS#'

        temp = getattr(self.bot.rosterColumns, self.columnConversion[name])

        setattr(self.bot.rosterColumns, self.columnConversion[name], default)

        result = f'Changed name for {name} Role from `{temp}` to `{getattr(self.bot.rosterColumns, self.columnConversion[name])}`'

        await interaction.followup.send(result)

    @columngroup.command(name="set-extra", description="Sets/Adds a name for an extra stored column header")
    @app_commands.describe(name='The name/purpose of the extra column header', value='The new name to store')
    async def set_column_other(self, interaction: discord.Interaction, name: str, value: str):
        await interaction.response.defer(thinking=True)
        if (name == ''):
            await interaction.followup.send('ERROR: `name` cannot be empty')
            return
        if (value == ''):
            await interaction.followup.send('ERROR: `value` cannot be empty')
            return

        temp = self.bot.rosterColumns.others.get(name)
        
        self.bot.rosterColumns.others[name] = value

        result = ''
        if temp:
            result = f'Changed header for {name} Column from `{temp}` to `{self.bot.rosterColumns.others[name]}`'
        else:
            result = f'Created header for {name} Column: `{self.bot.rosterColumns.others[name]}`'

        await interaction.followup.send(result)

    @columngroup.command(name="remove-extra", description="Removes an extra stored column header from storage")
    @app_commands.describe(name='The name/purpose of the extra column header')
    async def remove_column_other(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(thinking=True)
        if (name == ''):
            await interaction.followup.send('ERROR: `name` cannot be empty')
            return

        temp = self.bot.rosterColumns.others.get(name)

        if not temp:
            await interaction.followup.send(f'There is no {name} Column to remove from extra storage. Check existing headers with `/config column list extra`')
            return

        del self.bot.rosterColumns.others[name]
        result = f'Removed header name `{temp}` for {name} Column'

        await interaction.followup.send(result)

    @sheetgroup.command(name="list", description="Lists all stored Roster Sheet information")
    @app_commands.describe(filter='How to filter the results')
    async def list_sheets(self, interaction: discord.Interaction, filter: Literal['all', 'default', 'extra']):
        await interaction.response.defer(thinking=True)

        result = ''
        if (filter in ['all', 'default']):
            result = result + "These are the default Sheet names stored in The Glot:"

            for key, value in self.sheetConversion.items():
                result = result + f"\n* {key} Sheet: `{getattr(self.bot.rosterSheets, value)}`"

        if (filter in ['all', 'extra']):
            if self.bot.rosterSheets.others and len(self.bot.rosterSheets.others) > 0:
                result = result + '\n\nThese are the Extra Sheet names stored in The Glot:'
                for key, value in self.bot.rosterSheets.others.items():
                    result = result + f'\n* {key} Sheet: `{value}`'
            else:
                result = result + '\n\nThere are no Extra Sheet names stored in The Glot'
        
        result = result + '\n\n**IMPORTANT: Each Sheet should have a unique name to prevent issues with distinguishing between two Sheets**'
        
        await interaction.followup.send(result)

    @sheetgroup.command(name="set", description="Sets a name for a default stored Sheet")
    @app_commands.describe(name='The name/purpose of the Sheet', value='The new name to store')
    async def set_sheet(self, interaction: discord.Interaction, name: Literal['Full Roster', 'Current Roster'], value: str):
        await interaction.response.defer(thinking=True)
        if (name == ''):
            await interaction.followup.send('ERROR: `name` cannot be empty')
            return
        if (value == ''):
            await interaction.followup.send('ERROR: `value` cannot be empty')
            return

        temp = getattr(self.bot.rosterSheets, self.sheetConversion[name])
        
        setattr(self.bot.rosterSheets, self.sheetConversion[name], value.name)

        result = f'Changed name for {name} Sheet from `{temp}` to `{getattr(self.bot.rosterSheets, self.sheetConversion[name])}`'

        await interaction.followup.send(result)

    @sheetgroup.command(name="reset", description="Resets the name for a default stored Sheet to default")
    @app_commands.describe(name='The name/purpose of the Sheet')
    async def reset_sheet(self, interaction: discord.Interaction, name: Literal['Full Roster', 'Current Roster']):
        await interaction.response.defer(thinking=True)
        if (name == ''):
            await interaction.followup.send('ERROR: `name` cannot be empty')
            return

        default = name
        if (default == 'Full Roster'): default = 'Roster'
        if (default == 'Current Roster'): default = 'Current'

        temp = getattr(self.bot.rosterSheets, self.sheetConversion[name])

        setattr(self.bot.rosterSheets, self.sheetConversion[name], default)

        result = f'Changed name for {name} Role from `{temp}` to `{getattr(self.bot.rosterSheets, self.sheetConversion[name])}`'

        await interaction.followup.send(result)

    @sheetgroup.command(name="set-extra", description="Sets/Adds a name for an extra stored Sheet")
    @app_commands.describe(name='The name/purpose of the extra Sheet', value='The new name to store')
    async def set_sheet_other(self, interaction: discord.Interaction, name: str, value: str):
        await interaction.response.defer(thinking=True)
        if (name == ''):
            await interaction.followup.send('ERROR: `name` cannot be empty')
            return
        if (value == ''):
            await interaction.followup.send('ERROR: `value` cannot be empty')
            return

        temp = self.bot.rosterSheets.others.get(name)
        
        self.bot.rosterSheets.others[name] = value

        result = ''
        if temp:
            result = f'Changed header for {name} Sheet from `{temp}` to `{self.bot.rosterSheets.others[name]}`'
        else:
            result = f'Created header for {name} Sheet: `{self.bot.rosterSheets.others[name]}`'

        await interaction.followup.send(result)

    @sheetgroup.command(name="remove-extra", description="Removes an extra stored Sheet from storage")
    @app_commands.describe(name='The name/purpose of the extra Sheet')
    async def remove_sheet_other(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(thinking=True)
        if (name == ''):
            await interaction.followup.send('ERROR: `name` cannot be empty')
            return

        temp = self.bot.rosterSheets.others.get(name)

        if not temp:
            await interaction.followup.send(f'There is no {name} Sheet to remove from extra storage. Check existing headers with `/config sheet list extra`')
            return

        del self.bot.rosterSheets.others[name]
        result = f'Removed header name `{temp}` for {name} Sheet'

        await interaction.followup.send(result)

async def setup(bot: Glot):
    await bot.add_cog(ConfigCog(bot), guild=bot.currentGuild)