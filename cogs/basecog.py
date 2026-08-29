import discord
from discord import app_commands
from discord.ext import commands
from glot import Glot
import numpy as np
import pandas as pd
import fitz
from io import BytesIO
import authenticate
from cogs.sheetscog import verify

class BaseCog(commands.Cog):
    def __init__(self, bot: Glot):
        self.bot = bot
        id_command = app_commands.Command(
            name="print-ids",
            callback= self.print_ids,
            guild_ids=[bot.currentGuild.id],
            description="Prints out a list of members and their ids for later use"
        )
        bot.tree.add_command(id_command, guild=bot.currentGuild)
        self.preview_ctx_menu = app_commands.ContextMenu(
            name='Create File Preview',
            callback=self.force_preview,
            guild_ids=[bot.currentGuild.id]
        )
        bot.tree.add_command(self.preview_ctx_menu, guild=bot.currentGuild)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.preview_ctx_menu.name, type=self.preview_ctx_menu.type)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # if message.guild.name != "Bot Testing": return

        if message.author == self.bot.user: return
        # if message.author == client.user: return

        if isinstance(message.channel, discord.DMChannel):
            dm = self.bot.get_channel(1414317415751356587)
            await message.forward(dm)
            return
        # if message.channel.id != 1373362239532302399: return
        channel = message.channel.name
        if channel == "verifications":
            await self.normal_verify(message)
            return
        elif channel == "bot-commands":
            # await self.bot.process_commands(message)
            return
        attachments = filter(lambda a: a.content_type == "application/pdf", message.attachments)
        if (attachments):
            for a in attachments:
                await file_preview(message, a)

    async def normal_verify(self, message: discord.Message):
        user = message.author
        id = user.id
        email = message.content.strip().lower()

        response = await verify(self.bot, user, email, False)
        await message.reply(response)

    @app_commands.checks.has_permissions(administrator=True)
    async def print_ids(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        members = list(self.bot.currentGuild.members)

        members.sort(key= lambda member: " ".join([" ".join(member.display_name.split(" ")[1:]),member.display_name.split(" ")[0]]))

        result = 'Member\t|\tID'

        for member in members:
            result = result + f'\n{member.display_name}\t{member.id}'

        await interaction.followup.send(result, ephemeral=True)

    @app_commands.checks.has_permissions(administrator=True)
    async def force_preview(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer(thinking=True, ephemeral=True)
        attachments = filter(lambda a: a.content_type == "application/pdf", message.attachments)
        if (attachments): 
            for a in attachments:
                await file_preview(message, a)
            await interaction.followup.send('All Done!', ephemeral=True)
            return
        await interaction.followup.send('No PDF File to Preview...', ephemeral=True)

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error : commands.CommandError):
    #     if isinstance(error, commands.errors.CheckFailure):
    #         await ctx.reply("Sorry, you don't have permission to run that command")
    #     elif isinstance(error, commands.errors.TooManyArguments):
    #         await ctx.reply("ERROR: Too many arguments; I don't know what to do with this")
    #     elif isinstance(error, commands.errors.MissingRequiredArgument):
    #         await ctx.reply(f"ERROR: Missing required argument `{error.param}`")
    #     else:
    #         await ctx.reply(f"{error}")


async def setup(bot: Glot):
    await bot.add_cog(BaseCog(bot), guild=bot.currentGuild)


async def file_preview(message: discord.Message, file: discord.Attachment):
    try:
        stream = await file.read()

        with fitz.open(stream=stream) as pdf:
            attachments = []
            num = 1
            for page in pdf.pages(stop=10):
                img = page.get_pixmap().tobytes()

                with BytesIO(img) as file_like:
                    f = discord.File(fp=file_like,filename=f"page{num}.png")
                    attachments.append(f)

                num = num + 1
            if pdf.page_count > 10:
                await message.reply(content="Sorry, I can only preview the first 10 pages:",files=attachments, mention_author=False)
            else:
                await message.reply(files=attachments, mention_author=False)
    except Exception as e:
        print(f"Encountered {type(e)}")