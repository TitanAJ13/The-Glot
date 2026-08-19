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
        update_command = app_commands.Command(
            name="update-roles",
            callback= self.update,
            guild_ids=[bot.currentGuild.id],
            description="Sync user roles from the Roster Sheet"
        )
        bot.tree.add_command(update_command, guild=bot.currentGuild)
        verify_command = app_commands.Command(
            name="verify",
            callback= self.verify_admin,
            guild_ids=[bot.currentGuild.id],
            description="Verify Members without the #verifications channel"
        )
        bot.tree.add_command(verify_command, guild=bot.currentGuild)

    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(roles="The kinds of roles to update")
    async def update(self, interaction: discord.Interaction, roles: Literal["all", "voice-parts", "alumni", "pantherhythms", "tour"]):
        service = authenticate.callService("sheets")
        result = (
            service.spreadsheets().values()
            .get(spreadsheetId=self.bot.roster_id, range="Roster", majorDimension="ROWS", valueRenderOption="FORMATTED_VALUE")
            .execute()
        )
        roster = result.get("values", [])

        data = pd.DataFrame(roster)
        pittIndex = pd.Index(data.iloc[0]).get_loc("Pitt Email")
        backupIndex = pd.Index(data.iloc[0]).get_loc("Personal Email")
        data.iloc[:,pittIndex] = data.iloc[:,pittIndex].replace('', np.nan).fillna(data.iloc[:,backupIndex])
        data.set_index(pittIndex, inplace=True)
        data.columns = data.iloc[0]
        data.drop(data.index[0],inplace=True)

        modified_users = []

        (rows, cols) = data.shape
        for i in range(rows):
            row = data.index[i]
            id = data.loc[row, "Discord ID"]
            if not id or math.isnan(float(id)):
                continue
            user = interaction.guild.get_member(int(id))
            if not user:
                continue

            changed = False

            if (roles in ["all", "voice-parts"]):
                part = data.loc[row, "Voice Part"]
                inactive = data.loc[row, "Tacet"] == 'TRUE'
                if (inactive):
                    part = "TACET"
                changed = changed or await self.updateVoicePart(user, part)

            if (roles in ["all", "alumni"]):
                alumni = data.loc[row, "Year"] == 'Alumni'
                changed = changed or await self.updateAlumni(user, alumni)

            if (roles in ["all", "pantherhythms"]):
                panther = data.loc[row, "Pantherhythms"] == 'TRUE'
                changed = changed or await self.updatePanther(user, panther)

            if (roles in ["all", "tour"]):
                tour = data.loc[row, "Tour"] == 'TRUE'
                changed = changed or await self.updateTour(user, tour)

            if (changed):
                modified_users.append(user.nick if user.nick else user.global_name)

        response = "The following users were updated:\n"
        if (len(modified_users) == 0):
            response = "No changes were made. Specified roles are up to date."
        else:
            for name in modified_users:
                response = response + f"* {name}\n"

        await interaction.response.send_message(response, ephemeral=True)


    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="The user to verify", email="Their Pitt Email on the Roster", override="Whether to override their previous verification (Optional)")
    async def verify_admin(self, interaction: discord.Interaction, user: discord.Member, email: str, override: Optional[bool] = False):
        response = await verify(self.bot, user, email, override)

        await interaction.response.send_message(response, ephemeral=True)


async def updateVoicePart(bot: Glot, user: discord.Member, part: str, reason: str = "Role Update"):
    section_role = discord.utils.find(lambda r: r.name == part, bot.all_roles)

    changed = False
    for role in [bot.t1, bot.t2, bot.bari, bot.bass, bot.tacet]:
        if (role in user.roles and role != section_role):
            await user.remove_roles(role, reason=reason)
            changed = True

    if (section_role not in user.roles):
        await user.add_roles(section_role, reason=reason)
        changed = True

    return changed


async def updateAlumni(bot: Glot, user: discord.Member, alumni: bool, reason: str = "Role Update"):
    alumni_role = discord.utils.find(lambda r: r.name == 'Alumni', bot.all_roles)

    if (alumni_role not in user.roles and alumni):
        await user.add_roles(alumni_role, reason=reason)
        return True
    elif (alumni_role in user.roles and not alumni):
        await user.remove_roles(alumni_role, reason=reason)
        return True

    return False

async def updatePanther(bot: Glot, user: discord.Member, panther: bool, reason: str = "Role Update"):
    panther_role = discord.utils.find(lambda r: r.name == 'Pantherhythms', bot.all_roles)

    if (panther_role not in user.roles and panther):
        await user.add_roles(panther_role, reason=reason)
        return True
    elif (panther_role in user.roles and not panther):
        await user.remove_roles(panther_role, reason=reason)
        return True

    return False

async def updateTour(bot: Glot, user: discord.Member, tour: bool, reason: str = "Role Update"):
    tour_role = discord.utils.find(lambda r: r.name == 'Tour', bot.all_roles)

    if (tour_role not in user.roles and tour):
        await user.add_roles(tour_role, reason=reason)
        return True
    elif (tour_role in user.roles and not tour):
        await user.remove_roles(tour_role, reason=reason)
        return True

    return False

async def verify(bot: Glot, user: discord.Member, email: str, override: bool):

    email = email.strip().lower()
    check = discord.utils.find(lambda r: r.name == "Nice Boi", bot.all_roles)
    if check in user.roles and not override:
        return "This user has already been verified"

    if not email.endswith('@pitt.edu'):
        email = email + '@pitt.edu'

    service = authenticate.callService("sheets")
    result = (
        service.spreadsheets().values()
        .get(spreadsheetId=bot.roster_id, range="Roster", majorDimension="ROWS", valueRenderOption="FORMATTED_VALUE")
        .execute()
    )
    roster = result.get("values", [])

    data = pd.DataFrame(roster)
    pittIndex = pd.Index(data.iloc[0]).get_loc("Pitt Email")
    backupIndex = pd.Index(data.iloc[0]).get_loc("Personal Email")
    idIndex = pd.Index(data.iloc[0]).get_loc("Discord ID")
    data.iloc[:,pittIndex] = data.iloc[:,pittIndex].replace('', np.nan).fillna(data.iloc[:,backupIndex])
    data.set_index(pittIndex, inplace=True)
    data.columns = data.iloc[0]
    data.drop(data.index[0],inplace=True)

    entry = data.loc[email]

    id = entry.get("Discord ID")

    if (not math.isnan(float(id)) and int(id) != user.id and not override):
        return "Sorry, that email has already been used to verify another member"

    first = entry.get("First Name")
    last = entry.get("Last Name")
    section = entry.get("Voice Part")
    if entry.get("Tacet") == 'TRUE':
        section = 'TACET'
    alumni = entry.get("Year") == 'Alumni'
    panther = entry.get("Pantherhythms") == 'TRUE'
    tour = entry.get("Tour") == 'TRUE'

    await updateVoicePart(bot, user, section, "Verification")
    await updateAlumni(bot, user, alumni, "Verification")
    await updatePanther(bot, user, panther, "Verification")
    await updateTour(bot, user, tour, "Verification")
    await user.add_roles(check, reason="Verification")

    # await user.edit(nick=f'{first} {last}', reason="Verification")

    col = numToCol(idIndex + 1)
    row = data.index.get_loc(email) + 2

    result2 = (
        service.spreadsheets().values()
        .update(spreadsheetId=bot.roster_id, range=f"Roster!{col}{row}", valueInputOption="RAW", body={'values': [[str(user.id)]]})
        .execute()
    )

    return "Verification completed! Welcome to the Glee Club! <:glee:1077812002107424879>"

def numToCol(value: int) -> str:
    result = []
    while value > 0:
        result.insert(0, chr(65 + (value - 1) % 26))
        value = value // 26
    return ''.join(result)

async def setup(bot: Glot):
    await bot.add_cog(SheetsCog(bot), guild=bot.currentGuild)