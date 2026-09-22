import discord
from discord import app_commands
from discord.ext import commands
from glot import Glot
import authenticate
import pandas as pd
import numpy as np
import math
from typing import Literal, Optional

class SheetsCog(commands.Cog):
    def __init__(self, bot: Glot):
        self.bot = bot
        self.update_command = app_commands.Command(
            name="update-roles",
            callback= self.update,
            guild_ids=[bot.currentGuild.id],
            description="Sync user roles from the Working PMGC Roster"
        )
        bot.tree.add_command(self.update_command, guild=bot.currentGuild)
        self.verify_command = app_commands.Command(
            name="verify",
            callback= self.verify_admin,
            guild_ids=[bot.currentGuild.id],
            description="Verify Members without the #verifications channel"
        )
        bot.tree.add_command(self.verify_command, guild=bot.currentGuild)
        self.nickname_command = app_commands.Command(
            name="send-nicknames",
            callback= self.send_nicknames,
            guild_ids=[bot.currentGuild.id],
            description="Sends members their official glicknames for introductions or otherwise"
        )
        bot.tree.add_command(self.nickname_command, guild=bot.currentGuild)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.update_command.name, guild=self.bot.currentGuild)
        self.bot.tree.remove_command(self.verify_command.name, guild=self.bot.currentGuild)
        self.bot.tree.remove_command(self.nickname_command.name, guild=self.bot.currentGuild)

    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(roles="The kinds of roles to update")
    async def update(self, interaction: discord.Interaction, roles: Literal["all", "voice-parts", "alumni", "pantherhythms", "tour"]):
        await interaction.response.defer(thinking=True)
        service = authenticate.callService("sheets", "v4")
        result = (
            service.spreadsheets().values()
            .get(spreadsheetId=self.bot.roster_id, range=self.bot.rosterSheets.fullRoster, majorDimension="ROWS", valueRenderOption="FORMATTED_VALUE")
            .execute()
        )
        roster = result.get("values", [])

        data = pd.DataFrame(roster)
        pittIndex = pd.Index(data.iloc[0]).get_loc(self.bot.rosterColumns.schoolEmail)
        backupIndex = pd.Index(data.iloc[0]).get_loc(self.bot.rosterColumns.personalEmail)
        data.iloc[:,pittIndex] = data.iloc[:,pittIndex].replace('', np.nan).fillna(data.iloc[:,backupIndex])
        data.set_index(pittIndex, inplace=True)
        data.columns = data.iloc[0]
        data.drop(data.index[0],inplace=True)
        data.index.name = self.bot.rosterColumns.schoolEmail
        data.index = data.index.str.lower()
        data.columns.name = ''
        data = data[data.index.notna() & (data.index != '')]

        modified_users = []

        (rows, cols) = data.shape
        for i in range(rows):
            row = data.index[i]
            id = data.loc[row, self.bot.rosterColumns.discordId]
            if not id or math.isnan(float(id)):
                continue
            user = interaction.guild.get_member(int(id))
            if not user:
                continue

            changed = False

            if (roles in ["all", "voice-parts"]):
                part = data.loc[row, self.bot.rosterColumns.voicePart]
                inactive = data.loc[row, self.bot.rosterColumns.tacet] == 'TRUE'
                if (inactive):
                    part = "TACET"
                changed = await self.updateVoicePart(user, part) or changed

            if (roles in ["all", "alumni"]):
                alumni = data.loc[row, self.bot.rosterColumns.gradeLevel] == 'Alumni'
                changed = await self.updateAlumni(user, alumni) or changed

            if (roles in ["all", "pantherhythms"]):
                panther = data.loc[row, self.bot.rosterColumns.pantherhythms] == 'TRUE'
                changed = await self.updatePanther(user, panther) or changed

            if (roles in ["all", "tour"]):
                tour = data.loc[row, self.bot.rosterColumns.tour] == 'TRUE'
                changed = await self.updateTour(user, tour) or changed

            if (changed):
                modified_users.append(user.nick if user.nick else user.global_name)

        response = "The following users were updated:\n"
        if (len(modified_users) == 0):
            response = "No changes were made. Specified roles are up to date."
        else:
            for name in modified_users:
                response = response + f"* {name}\n"

        await interaction.followup.send(response, ephemeral=True)


    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="The user to verify", email="Their Pitt Email on the Roster", override="Whether to override their previous verification (Optional)")
    async def verify_admin(self, interaction: discord.Interaction, user: discord.Member, email: str, override: Optional[bool] = False):
        await interaction.response.defer(thinking=True)
        response = await self.verify(user, email, override)

        await interaction.followup.send(response, ephemeral=True)

    @app_commands.checks.has_permissions(administrator=True)
    async def send_nicknames(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        service = authenticate.callService("sheets", "v4")
        result = (
            service.spreadsheets().values()
            .get(spreadsheetId=self.bot.roster_id, range=self.bot.rosterSheets.currentRoster, majorDimension="ROWS", valueRenderOption="FORMATTED_VALUE")
            .execute()
        )
        roster = result.get("values", [])

        data = pd.DataFrame(roster)
        pittIndex = pd.Index(data.iloc[0]).get_loc(self.bot.rosterColumns.schoolEmail)
        backupIndex = pd.Index(data.iloc[0]).get_loc(self.bot.rosterColumns.personalEmail)
        data.iloc[:,pittIndex] = data.iloc[:,pittIndex].replace('', np.nan).fillna(data.iloc[:,backupIndex])
        data.set_index(pittIndex, inplace=True)
        data.columns = data.iloc[0]
        data.drop(data.index[0],inplace=True)
        data.index.name = self.bot.rosterColumns.schoolEmail
        data.index = data.index.str.lower()
        data.columns.name = ''
        data = data[data.index.notna() & (data.index != '')]

        sent_users = []
        nope_users = {}

        response = "## Sent nicknames to:"
        (rows, cols) = data.shape
        for i in range(rows):
            row = data.index[i]
            id = data.loc[row, self.bot.rosterColumns.discordId]
            if not id or math.isnan(float(id)):
                continue
            user = interaction.guild.get_member(int(id))
            if not user:
                continue

            nickname = data.loc[row, self.bot.rosterColumns.nickname]
            if not nickname or nickname == '':
                continue

            try:
                await user.send(f"Hey there {user.mention}! Here's your glickname in case you forgot.\n\n**This is your only nickname and there are no fake nicknames. Please don't mention fake nicknames to the newbies.**\n\nGlickname: ```{nickname}```")
                sent_users.append(user.nick if user.nick else user.global_name)
                response = response + f"\n* {user.nick if user.nick else user.global_name}"
                await interaction.edit_original_response(content=response)
            except Exception as e:
                nope_users[user.nick if user.nick else user.global_name] = e

            

        if (len(sent_users) == 0):
            response = response + f"\nNo nicknames were sent. Please check the `{self.bot.rosterSheets.currentRoster}` sheet in the Working PMGC Roster"

        if (len(nope_users) > 0):
            response = response + '\n\n## Nicknames failed to send to:'
            for name, error in nope_users.items():
                response = response + f'\n* {name}: {error}'

        response = response + '\n\n*All Done!*'

        await interaction.edit_original_response(content=response)


    async def updateVoicePart(self, user: discord.Member, part: str, reason: str = "Role Update"):
        conversion = {
            "Tenor 1": self.bot.t1Role(),
            "Tenor 2": self.bot.t2Role(),
            "Baritone": self.bot.bariRole(),
            "Bass": self.bot.bassRole(),
            "TACET": self.bot.tacetRole()
        }

        section_role = conversion.get(part)
        if not section_role:
            return False

        changed = False
        for role in self.bot.voice_parts():
            if (role in user.roles and role != section_role):
                await user.remove_roles(role, reason=reason)
                changed = True

        if (section_role not in user.roles):
            await user.add_roles(section_role, reason=reason)
            changed = True

        return changed


    async def updateAlumni(self, user: discord.Member, alumni: bool, reason: str = "Role Update"):
        alumniRole = self.bot.alumniRole()

        if (alumniRole not in user.roles and alumni):
            await user.add_roles(alumniRole, reason=reason)
            return True
        elif (alumniRole in user.roles and not alumni):
            await user.remove_roles(alumniRole, reason=reason)
            return True

        return False

    async def updatePanther(self, user: discord.Member, panther: bool, reason: str = "Role Update"):
        pantherRole = self.bot.pantherRole()

        if (pantherRole not in user.roles and panther):
            await user.add_roles(pantherRole, reason=reason)
            return True
        elif (pantherRole in user.roles and not panther):
            await user.remove_roles(pantherRole, reason=reason)
            return True

        return False

    async def updateTour(self, user: discord.Member, tour: bool, reason: str = "Role Update"):
        tourRole = self.bot.tourRole()

        if (tourRole not in user.roles and tour):
            await user.add_roles(tourRole, reason=reason)
            return True
        elif (tourRole in user.roles and not tour):
            await user.remove_roles(tourRole, reason=reason)
            return True

        return False

    async def verify(self, user: discord.Member, email: str, override: bool):

        email = email.strip().lower()
        if self.bot.checkRole() in user.roles and not override:
            return "This user has already been verified"

        if not email.endswith('@pitt.edu'):
            email = email + '@pitt.edu'

        service = authenticate.callService("sheets", "v4")
        result = (
            service.spreadsheets().values()
            .get(spreadsheetId=self.bot.roster_id, range=self.bot.rosterSheets.fullRoster, majorDimension="ROWS", valueRenderOption="FORMATTED_VALUE")
            .execute()
        )
        roster = result.get("values", [])

        data = pd.DataFrame(roster)
        pittIndex = pd.Index(data.iloc[0]).get_loc(self.bot.rosterColumns.schoolEmail)
        backupIndex = pd.Index(data.iloc[0]).get_loc(self.bot.rosterColumns.personalEmail)
        idIndex = pd.Index(data.iloc[0]).get_loc(self.bot.rosterColumns.discordId)
        data.iloc[:,pittIndex] = data.iloc[:,pittIndex].replace('', np.nan).fillna(data.iloc[:,backupIndex])
        data.set_index(pittIndex, inplace=True)
        data.columns = data.iloc[0]
        data.drop(data.index[0],inplace=True)
        data.index.name = self.bot.rosterColumns.schoolEmail
        data.index = data.index.str.lower()
        data.columns.name = ''
        data = data[data.index.notna() & (data.index != '')]
    
        if email not in data.index:
            return f"Sorry, that email isn't in my system. Please check for typos or wait for {self.bot.boardRole().mention} to update the Roster"
        
        entry = data.loc[email]

        id = entry.get(self.bot.rosterColumns.discordId)

        if (not math.isnan(float(id)) and int(id) != user.id and not override):
            return "Sorry, that email has already been used to verify another member"

        first = entry.get(self.bot.rosterColumns.firstName)
        last = entry.get(self.bot.rosterColumns.lastName)
        section = entry.get(self.bot.rosterColumns.voicePart)
        if entry.get(self.bot.rosterColumns.tacet) == 'TRUE':
            section = 'TACET'

        if not first or first == '' or not last or last == '' or not section or section == '':
            return f"Sorry, we're still adding you into the system. Please wait for {self.bot.boardRole().mention} to update the Roster, then try again."
        
        alumni = entry.get(self.bot.rosterColumns.gradeLevel) == 'Alumni'
        panther = entry.get(self.bot.rosterColumns.pantherhythms) == 'TRUE'
        tour = entry.get(self.bot.rosterColumns.tour) == 'TRUE'

        await self.updateVoicePart(user, section, "Verification")
        await self.updateAlumni(user, alumni, "Verification")
        await self.updatePanther(user, panther, "Verification")
        await self.updateTour(user, tour, "Verification")
        await user.add_roles(self.bot.checkRole(), reason="Verification")

        await user.edit(nick=f'{first} {last}', reason="Verification")

        col = self.numToCol(idIndex + 1)
        row = data.index.get_loc(email) + 2

        result2 = (
            service.spreadsheets().values()
            .update(spreadsheetId=self.bot.roster_id, range=f"{self.bot.rosterSheets.fullRoster}!{col}{row}", valueInputOption="RAW", body={'values': [[str(user.id)]]})
            .execute()
        )

        return "Verification completed! Welcome to the Glee Club! <:glee:1077812002107424879>"

    def numToCol(self, value: int) -> str:
        result = []
        while value > 0:
            result.insert(0, chr(65 + (value - 1) % 26))
            value = value // 26
        return ''.join(result)

async def setup(bot: Glot):
    await bot.add_cog(SheetsCog(bot), guild=bot.currentGuild)