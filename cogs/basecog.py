import discord
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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # if message.guild.name != "Bot Testing": return

        if message.author == self.bot.user: return
        # if message.author == client.user: return

        if isinstance(message.channel, discord.DMChannel):
            dm = self.bot.get_channel(1414317415751356587)
            message.forward(dm)
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

        # check = discord.utils.find(lambda r: r.name == "Nice Boi", self.bot.all_roles)
        # if check not in user.roles:
        #     if not email.endswith('@pitt.edu'):
        #         email = f'{email}@pitt.edu'

        #     service = authenticate.callService("sheets")
        #     result = (
        #         service.spreadsheets().values()
        #         .get(spreadsheetId=self.bot.roster_id, range="Roster", majorDimension="ROWS", valueRenderOption="FORMATTED_VALUE")
        #         .execute()
        #     )
        #     roster = result.get("values", [])

        #     data = pd.DataFrame(roster)
        #     data.set_index(3, inplace=True)
        #     data.columns = data.iloc[0]
        #     data.drop(data.index[0],inplace=True)

        #     entry = data.loc[email]

        #     id = entry.get("Discord ID")
        #     if (not np.isnan(id)):
        #         await message.reply("Sorry, that email has already been used to verify another member")
        #     else:
        #         first = entry.get("First Name")
        #         last = entry.get("Last Name")
        #         section = entry.get("Voice Part")
        #         inactive = entry.get("Tacet") == "TRUE"
        #         year = entry.get("Year")

        #         section_role = discord.utils.find(lambda r: r.name == section, self.bot.all_roles)
        #         # print(f"Role type: {section_role}")

        #         roles = user.roles

        #         # Remove Incorrect Roles

        #         if (self.bot.t1 in roles and (self.bot.t1 != section_role or inactive)):
        #             print("removing t1")
        #             await user.remove_roles(self.bot.t1,reason="Verification")
        #         if (self.bot.t2 in roles and (self.bot.t2 != section_role or inactive)):
        #             print("removing t2")
        #             await user.remove_roles(self.bot.t2,reason="Verification")
        #         if (self.bot.bari in roles and (self.bot.bari != section_role or inactive)):
        #             print("removing bari")
        #             await user.remove_roles(self.bot.bari,reason="Verification")
        #         if (self.bot.bass in roles and (self.bot.bass != section_role or inactive)):
        #             print("removing bass")
        #             await user.remove_roles(self.bot.bass,reason="Verification")

        #         # Add Correct Roles
        #         await user.add_roles(check,self.bot.tacet if inactive else section_role,reason="Verification")
        #         if (year == "Alumni" and self.bot.alumni not in roles):
        #             await user.add_roles(self.bot.alumni, reason="Verification")

        #         # Edit Server Nickname
        #         await user.edit(nick=f"{first} {last}")

        #         # Respond to message
        #         await message.reply("Verification completed! Welcome to the Glee Club! <:glee:1077812002107424879>")

    @commands.command(name='preview', help='Generate file preview for a previously sent message')
    @commands.has_guild_permissions(administrator=True)
    async def force_preview(self, ctx: commands.Context, channelId:int, messageId: int):
        message = await self.bot.get_channel(channelId).fetch_message(messageId)

        attachments = filter(lambda a: a.content_type == "application/pdf", message.attachments)
        if (attachments): 
            for a in attachments:
                await file_preview(message, a)

    @commands.command(name='ids', help="Prints out a list of members and their ids for later use")
    @commands.has_guild_permissions(administrator=True)
    async def print_ids(self, ctx: commands.Context):
        members = list(self.bot.currentGuild.members)

        members.sort(key= lambda member: " ".join([" ".join(member.display_name.split(" ")[1:]),member.display_name.split(" ")[0]]))

        for member in members:
            print(f'{member.display_name}\t{member.id}')

    # @commands.command(name='verify', help="Verifies new members")
    # @commands.has_guild_permissions(administrator=True)
    # async def verify_admin(self, ctx : commands.Context, id: int, email : str):
    #     print("Command run")

    #     user = discord.utils.find(lambda u:u.id == id, ctx.guild.members)

    #     if ctx.channel.id != 1373362239532302399: return
    #     email = email.strip().lower()

    #     check = discord.utils.find(lambda r: r.name == "Nice Boi", self.bot.all_roles)
    #     if check not in user.roles:
    #         if not email.endswith('@pitt.edu'):
    #             email = f'{email}@pitt.edu'

    #         service = authenticate.callService("sheets")
    #         result = (
    #             service.spreadsheets().values()
    #             .get(spreadsheetId=self.bot.roster_id, range="Roster", majorDimension="ROWS", valueRenderOption="FORMATTED_VALUE")
    #             .execute()
    #         )
    #         roster = result.get("values", [])

    #         data = pd.DataFrame(roster)
    #         pittIndex = pd.Index(data.iloc[0]).get_loc("Pitt Email")
    #         backupIndex = pd.Index(data.iloc[0]).get_loc("Personal Email")
    #         data.iloc[:,pittIndex] = data.iloc[:,pittIndex].replace('', np.nan).fillna(data.iloc[:,backupIndex])
    #         data.set_index(pittIndex, inplace=True)
    #         data.columns = data.iloc[0]
    #         data.drop(data.index[0],inplace=True)

    #         entry = data.loc[email]
    #         # print("Found email")
    #         first = entry.get("First Name")
    #         # print("Found first name")
    #         last = entry.get("Last Name")
    #         # print("Found last name")
    #         section = entry.get("Voice Part")
    #         if (entry.get("Tacet") == 'TRUE'):
    #             section = 'TACET'
    #         # print("Found voice part")
    #         alumni = entry.get("Year") == 'Alumni'
    #         panther = entry.get("Pantherhythms") == 'TRUE'
    #         tour = entry.get("Tour") == 'TRUE'

    #         print("Adding roles")
    #         await self.updateRoles(user, section, alumni, panther, tour)

    #         print("editting nickname")
    #         await user.edit(nick=f"{first} {last}", reason="Verification")

    #         await ctx.reply("Verification completed! Welcome to the Glee Club! <:glee:1077812002107424879>")
    #         # try:
    #         # except:
    #         #     await ctx.reply("Sorry, that email wasn't found in my system. Please check for typos or wait a few days for admins to update the system.")

    async def updateRoles(self, user: discord.Member, part: str, alumni: bool, panther: bool, tour: bool):
        section_role = discord.utils.find(lambda r: r.name == part, self.bot.all_roles)

        for role in [self.bot.t1, self.bot.t2, self.bot.bari, self.bot.bass, self.bot.tacet]:
            if (role in user.roles and role != section_role):
                await user.remove_roles(role, reason="Verifiation")

        if (section_role not in user.roles):
            await user.add_roles(section_role, reason="Verifiation")

        alumni_role = discord.utils.find(lambda r: r.name == 'Alumni', self.bot.all_roles)
        
        if (alumni_role not in user.roles and alumni):
            await user.add_roles(alumni_role, reason="Verifiation")
        elif (alumni_role in user.roles and not alumni):
            await user.remove_roles(alumni_role, reason="Verifiation")

        panther_role = discord.utils.find(lambda r: r.name == 'Pantherhythms', self.bot.all_roles)
        
        if (panther_role not in user.roles and panther):
            await user.add_roles(panther_role, reason="Verifiation")
        elif (panther_role in user.roles and not panther):
            await user.remove_roles(panther_role, reason="Verifiation")

        tour_role = discord.utils.find(lambda r: r.name == 'Tour', self.bot.all_roles)
        
        if (tour_role not in user.roles and tour):
            await user.add_roles(tour_role, reason="Verifiation")
        elif (tour_role in user.roles and not tour):
            await user.remove_roles(tour_role, reason="Verifiation")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error : commands.CommandError):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.reply("Sorry, you don't have permission to run that command")
        elif isinstance(error, commands.errors.TooManyArguments):
            await ctx.reply("ERROR: Too many arguments; I don't know what to do with this")
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.reply(f"ERROR: Missing required argument `{error.param}`")
        else:
            await ctx.reply(f"{error}")


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