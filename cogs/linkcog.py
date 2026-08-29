from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
import requests
from cogs.helper import handleResponse, BearerAuth
from glot import Glot

class LinkCog(commands.Cog):

    def __init__(self, bot: Glot) -> None:
        self.bot: Glot = bot
        self.URL = lambda: self.bot.glanvasURL + 'links/'

    async def cog_load(self):
        glanvasGroup = self.bot.tree.get_command('glanvas', guild=self.bot.currentGuild)
        if isinstance(glanvasGroup, app_commands.Group):
            group = app_commands.Group(name='link', description='Make changes to the links on the Glanvas')

            @group.command(name="add", description="Adds a new link")
            @app_commands.describe(type='Type of link', title='Link display title', url='The actual URL', position='Optional: The position to insert it into')
            async def add_link(interaction: discord.Interaction, type: Literal['internal','external','file','music','page','form'], title: str, url: str, position: Optional[int] = None):
                await interaction.response.defer(thinking=True)
                if (position is not None and position < 1):
                    await interaction.followup.send('ERROR: `position` cannot be less than 1')
                    return
                if (title == ''):
                    await interaction.followup.send('ERROR: `title` cannot be empty')
                    return
                if (url == ''):
                    await interaction.followup.send('ERROR: `url` cannot be empty')
                    return
                if (type == 'internal' and url not in ['home', 'announcements', 'modules']):
                    await interaction.followup.send("ERROR: Internal URLs can only be `home`, `modules`, or `announcements`.")
                    return
                if (type == 'external' and url[:8] != 'https://'):
                    await interaction.followup.send("ERROR: External URLs must start with `https://`.")
                    return
                

                title = title.strip()
                url = url.strip()
                linkObj = {
                    'display_name': title,
                    'type': type,
                    'url': url,
                    'position': position
                }


                response = requests.post(self.URL(), json=linkObj, auth=BearerAuth())
                result = handleResponse(response, 'Successfully added the link')
                await interaction.followup.send(result)


            @group.command(name="remove", description="Removes an existing link")
            @app_commands.describe(position='The position of the link in the list')
            async def remove_link(interaction: discord.Interaction, position: int):
                await interaction.response.defer(thinking=True)
                if (position < 1):
                    await interaction.followup.send('ERROR: `position` cannot be less than 1')
                    return

                response = requests.delete(self.URL(), json={'position': position}, auth=BearerAuth())
                result = handleResponse(response, 'Successfully removed the link')
                await interaction.followup.send(result)

            @group.command(name="edit", description="Edits an existing link")
            @app_commands.describe(position='The position of the link to edit', type='Type of link', title='Link display title', url='The actual URL')
            async def edit_link(interaction: discord.Interaction, position: int, type: Optional[Literal['internal','external','file','music','page','form']] = None, title: Optional[str] = None, url: Optional[str] = None):
                await interaction.response.defer(thinking=True)
                if (position < 1):
                    await interaction.followup.send('ERROR: `position` cannot be less than 1')
                    return
                if (type is None and title is None and url is None):
                    await interaction.followup.send('ERROR: at least one of `type`, `title`, or `url` must be defined')
                    return
                if (title is not None and title == ''):
                    await interaction.followup.send('ERROR: `title` cannot be empty if it is used')
                    return
                if (url is not None and url == ''):
                    await interaction.followup.send('ERROR: `url` cannot be empty if it is used')
                    return
                
                changes = {}

                if (type is not None):
                    changes['type'] = type
                if (title is not None):
                    changes['title'] = title
                if (url is not None):
                    changes['url'] = url

                linkObj = {
                    'position': position,
                    'changes': changes
                }

                response = requests.patch(self.URL(), json=linkObj, auth=BearerAuth())
                result = handleResponse(response, 'Successfully edited the link')
                await interaction.followup.send(result)

            @group.command(name="move", description="Move a link to a different position")
            @app_commands.describe(position1='The current position of the link', position2='The position to end up at')
            async def move_link(interaction: discord.Interaction, position1: int, position2: int):
                await interaction.response.defer(thinking=True)
                if (position1 < 1):
                    await interaction.followup.send('ERROR: `position1` cannot be less than 1')
                    return
                if (position2 < 1):
                    await interaction.followup.send('ERROR: `position2` cannot be less than 1')
                    return
                
                response = requests.put(self.URL(), json={'position': position1, 'position2': position2}, auth=BearerAuth())
                result = handleResponse(response, 'Successfully moved the link')
                await interaction.followup.send(result)

            glanvasGroup.add_command(group)

async def setup(bot: Glot):
    await bot.add_cog(LinkCog(bot), guild=bot.currentGuild)