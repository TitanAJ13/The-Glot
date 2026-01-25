import discord
from discord import app_commands
from discord.ext import commands
from glot import Glot
import authenticate
import pandas as pd
from typing import Literal, Optional

class SheetsCog(commands.Cog):
    def __init__(self, bot: Glot):
        self.bot = bot
        update_command = app_commands.Command(
            name="update-roles",
            callback= self.update,
            guild_ids=[bot.currentGuild.id]
        )
        bot.tree.add_command(update_command, guild=bot.currentGuild)

    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(roles="The kinds of roles to update")
    async def update(self, interaction: discord.Interaction, type: Literal["all", "voice-parts", "alumni", "pantherhythms"]):
        service = authenticate.callService("sheets")
        result = (
            service.spreadsheets().values()
            .get(spreadsheetId=self.bot.roster_id, range="Roster", majorDimension="ROWS", valueRenderOption="FORMATTED_VALUE")
            .execute()
        )
        roster = result.get("values", [])

        data = pd.DataFrame(roster)
        data.set_index(3, inplace=True)
        data.columns = data.iloc[0]
        data.drop(data.index[0],inplace=True)


        (rows, cols) = data.shape
        for i in range(rows):
            row = data.index[i]
            id = data.loc[row, "Discord ID"]
            if not id:
                continue
            user = interaction.guild.get_member(int(id))

            if (type in ["all", "voice-parts"]):
                part = data.loc[row, "Voice Part"]
                inactive = data.loc[row, "Tacet"] == 'TRUE'
                if (inactive):
                    part = "TACET"
                await self.updateVoicePart(user, data.loc[row, "Voice Part"])


    async def updateVoicePart(self, user: discord.Member, part: str):
        section_role = discord.utils.find(lambda r: r.name == part, self.bot.all_roles)

        for role in [self.bot.t1, self.bot.t2, self.bot.bari, self.bot.bass, self.bot.tacet]:
            if (role in user.roles and role != section_role):
                await user.remove_roles(role, reason="Role Update")

async def setup(bot: Glot):
    pass