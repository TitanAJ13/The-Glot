import os
from typing import Sequence
# from typing import Any, Literal, Optional
import discord
from discord.ext import commands
from discord.guild import Guild
from discord.role import Role

class Glot(commands.Bot):
    glanvasURL: str = ''
    currentGuild: Guild = None
    all_roles: Sequence[Role]
    t1: Role
    t2: Role
    bari: Role
    bass: Role
    tacet: Role
    alumni: Role
    roster_id: str = ''

    def setGuild(self, guild: Guild):
        self.currentGuild = guild
        self.all_roles = self.currentGuild.roles
        self.t1 = discord.utils.find(lambda r:r.name == "Tenor 1", self.all_roles)
        self.t2 = discord.utils.find(lambda r:r.name == "Tenor 2", self.all_roles)
        self.bari = discord.utils.find(lambda r:r.name == "Baritone", self.all_roles)
        self.bass = discord.utils.find(lambda r:r.name == "Bass", self.all_roles)
        self.tacet = discord.utils.find(lambda r:r.name == "TACET", self.all_roles)
        self.alumni = discord.utils.find(lambda r:r.name == "Alumni", self.all_roles)
