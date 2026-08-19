from typing import Any, Optional
import discord
from discord import app_commands
from discord import ui
from discord import utils
from discord.ext import commands
from datetime import date, datetime, timezone
import re
import markdown
import requests
from cogs.md_extensions import StrikethroughExtension
from cogs.helper import BearerAuth
from glot import Glot

def utc_to_local(time: datetime):
        return time.replace(tzinfo=timezone.utc).astimezone(tz=None)

class AnnouncementCog(commands.Cog):
    def __init__(self, bot: Glot, base) -> None:
        self.bot: Glot = bot
        self.URL: str = base + "announcements/"
        self.post_ctx_menu = app_commands.ContextMenu(
            name='Post To Glanvas',
            callback=self.post_announcement,
            guild_ids=[bot.currentGuild.id]
        )
        self.edit_ctx_menu = app_commands.ContextMenu(
            name='Update Post',
            callback=self.edit_announcement,
            guild_ids=[bot.currentGuild.id]
        )
        self.bot.tree.add_command(self.post_ctx_menu, guild=bot.currentGuild)
        self.bot.tree.add_command(self.edit_ctx_menu, guild=bot.currentGuild)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.post_ctx_menu.name, type=self.post_ctx_menu.type)
        self.bot.tree.remove_command(self.edit_ctx_menu.name, type=self.edit_ctx_menu.type)

    # group = app_commands.Group(name='announcement', description='Make changes to the announcements on the Glanvas', guild_ids=[1378895395253387344])
    
    # @group.command(name="add", description="Adds a new link")
    # @app_commands.describe(type='Type of link', title='Link display title', url='The actual URL', position='Optional: The position to insert it into')
    # async def add_link(self, interaction: discord.Interaction, type: Literal['internal','external','file','music','page','form'], title: str, url: str, position: Optional[int] = None):
    #     if (position is not None and position < 1):
    #         await interaction.response.send_message('ERROR: `position` cannot be less than 1')
    #         return
    #     if (title == ''):
    #         await interaction.response.send_message('ERROR: `title` cannot be empty')
    #         return
    #     if (url == ''):
    #         await interaction.response.send_message('ERROR: `url` cannot be empty')
    #         return
    #     if (type == 'internal' and url not in ['home', 'announcements', 'modules']):
    #         await interaction.response.send_message("ERROR: Internal URLs can only be `home`, `modules`, or `announcements`.")
    #         return
    #     if (type == 'external' and url[:8] != 'https://'):
    #         await interaction.response.send_message("ERROR: External URLs must start with `https://`.")
    #         return
    #     title = title.strip()
    #     url = url.strip()
    #     linkObj = {
    #         'display_name': title,
    #         'type': type,
    #         'url': url,
    #         'position': position
    #     }
    #     response = requests.post(self.URL, json=linkObj).json()
    #     if (response.status == 'success'):
    #         await interaction.response.send_message('Succesfully posted link')
    #     else:
    #         await interaction.response.send_message(f'ERROR: {response.message}')

    # @app_commands.guilds(614104404102086658)
    @app_commands.checks.has_permissions(administrator=True)
    async def post_announcement(self, interaction: discord.Interaction, message: discord.Message):
        content = message.content

        # Roles
        for match in re.findall(r'<@&.+?>',content):
            id = match.split("&")[1][:-1]
            role = message.guild.get_role(int(id))
            if role.color != discord.Color.default():
                (r, g, b) = role.color.to_rgb()
                replacement = f'<span class="mention" style="color: rgb{(r, g, b)}; background-color: rgba{(r, g, b, 0.3)}">@{role.name}</span>'
                content = content.replace(match, replacement)
            else:
                replacement = f'<span class="mention">@{role.name}</span>'
                content = content.replace(match, replacement)

        # Mentions
        for match in re.findall(r'<@.+?>',content):
            id = match.split("@")[1][:-1]
            member = message.guild.get_member(int(id))
            replacement = f'<span class="mention">@{member.nick if member.nick is not None else member.global_name}</span>'
            content = content.replace(match, replacement)

        # Channels
        for match in re.findall(r'<#.+?>',content):
            id = match.split("#")[1][:-1]
            channel = message.guild.get_channel_or_thread(int(id))
            replacement = f'<span class="mention">#{channel.name}</span>'
            content = content.replace(match, replacement)

        # Custom Emojis
        for match in re.findall(r'<:.+?:.+?>',content):
            id = match.split(":")[2][:-1]
            url = message.guild.get_emoji(int(id)).url
            replacement = f'<img class="emoji" src="{url}">'
            content = content.replace(match, replacement)

        # @here and @everyone
        content = content.replace("@here", '<span class="mention">@here</span>')
        content = content.replace("@everyone", '<span class="mention">@everyone</span>')

        # Convert from markdown
        md = markdown.Markdown(extensions=['fenced_code', 'sane_lists', 'nl2br', StrikethroughExtension()], tab_length=2)
        md.parser.blockprocessors.deregister('setextheader')
        content = md.convert(content)

        author = message.author
        if (author.nick is None):
            author = author.global_name
        else:
            author = author.nick

        messageData = {
            'id': message.id,
            'content': content,
            'author': author,
            'date_posted': utc_to_local(message.created_at).isoformat(),
            'url': self.URL,
            'avatar': message.author.display_avatar.url
        }

        modal = PromptTitle()
        modal.messageData = messageData
        
        await interaction.response.send_modal(modal)


    @app_commands.checks.has_permissions(administrator=True)
    async def edit_announcement(self, interaction: discord.Interaction, message: discord.Message):
        content = message.content

        # Roles
        for match in re.findall(r'<@&.+?>',content):
            id = match.split("&")[1][:-1]
            role = message.guild.get_role(int(id))
            if role.color != discord.Color.default():
                (r, g, b) = role.color.to_rgb()
                replacement = f'<span class="mention" style="color: rgb{(r, g, b)}; background-color: rgba{(r, g, b, 0.3)}">@{role.name}</span>'
                content = content.replace(match, replacement)
            else:
                replacement = f'<span class="mention">@{role.name}</span>'
                content = content.replace(match, replacement)

        # Mentions
        for match in re.findall(r'<@.+?>',content):
            id = match.split("@")[1][:-1]
            member = message.guild.get_member(int(id))
            replacement = f'<span class="mention">@{member.nick if member.nick is not None else member.global_name}</span>'
            content = content.replace(match, replacement)

        # Channels
        for match in re.findall(r'<#.+?>',content):
            id = match.split("#")[1][:-1]
            channel = message.guild.get_channel_or_thread(int(id))
            replacement = f'<span class="mention">#{channel.name}</span>'
            content = content.replace(match, replacement)

        # Custom Emojis
        for match in re.findall(r'<:.+?:.+?>',content):
            id = match.split(":")[2][:-1]
            url = message.guild.get_emoji(int(id)).url
            replacement = f'<img class="emoji" src="{url}">'
            content = content.replace(match, replacement)

        # @here and @everyone
        content = content.replace("@here", '<span class="mention">@here</span>')
        content = content.replace("@everyone", '<span class="mention">@everyone</span>')

        # Convert from markdown
        md = markdown.Markdown(extensions=['fenced_code', 'sane_lists', 'nl2br', StrikethroughExtension()], tab_length=2)
        md.parser.blockprocessors.deregister('setextheader')
        content = md.convert(content)

        messageData = {
            'id': message.id,
            'content': content,
            'url': self.URL,
            'avatar': message.author.display_avatar.url
        }

        modal = PromptEditTitle()
        modal.messageData = messageData
        
        await interaction.response.send_modal(modal)

    

class PromptTitle(ui.Modal, title="Post an Announcement"):
    messageData: dict[str, Any] = None

    display_name = ui.TextInput(label="Announcement Title", placeholder="New Announcement",required=True)

    async def on_submit(self, interaction: discord.Interaction):
        announcementObj = {
            "id": self.messageData['id'],
            "author": self.messageData['author'],
            "title": self.display_name.value,
            "date_posted": self.messageData['date_posted'],
            "content": self.messageData['content'],
            "avatar": self.messageData['avatar']
        }

        response = requests.post(self.messageData['url'], json=announcementObj, auth=BearerAuth()).json()

        # alert = ResponseAlert()
        if (response['status'] == 'success'):
            await interaction.response.send_message("Successfully posted the announcement!", ephemeral=True)
        else:
            await interaction.response.send_message(f"ERROR: {response['message']}", ephemeral=True)
            # alert.display.value = f'ERROR: {response['message']}'

        # await interaction.response.send_modal(alert)


class PromptEditTitle(ui.Modal, title="Update Posted Announcement"):
    messageData: dict[str, Any] = None

    label = ui.Label(text="Change Announcement Title", description="Leave blank if you don't want to change it.",
                     component=ui.TextInput(placeholder="New Title",required=False))

    async def on_submit(self, interaction: discord.Interaction):
        changes = {}

        newTitle = self.label.component.value

        if (newTitle is not None and newTitle != ''):
            changes["title"] = newTitle

        changes['content'] = self.messageData['content']
        changes['avatar'] = self.messageData['avatar']

        announcementObj = {
            "id": self.messageData['id'],
            "changes": changes
        }

        response = requests.patch(self.messageData['url'], json=announcementObj, auth=BearerAuth()).json()

        # alert = ResponseAlert()
        if (response['status'] == 'success'):
            await interaction.response.send_message("Successfully updated the announcement!", ephemeral=True)
        else:
            await interaction.response.send_message(f"ERROR: {response['message']}", ephemeral=True)
            # alert.display.value = f'ERROR: {response['message']}'

        # await interaction.response.send_modal(alert)


async def setup(bot: Glot):
    await bot.add_cog(AnnouncementCog(bot, bot.glanvasURL))