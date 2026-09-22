import os
from typing import Sequence, List, Dict
from collections.abc import Callable
# from typing import Any, Literal, Optional
import discord
from discord.ext import commands
from discord.guild import Guild
from discord.role import Role


class SpreadsheetColumns():
    firstName: str = "First Name"
    lastName: str = "Last Name"
    voicePart: str = "Voice Part"
    tacet: str = "Tacet"
    gradeLevel: str = "Year"
    pantherhythms: str = "Pantherhythms"
    tour: str = "Tour"
    schoolEmail: str = "Pitt Email"
    personalEmail: str = "Personal Email"
    discordId: str = "Discord ID"
    nickname: str = "Glickname"
    preferredName: str = "Preferred Name"
    concertName: str = "Concert Name"
    voiceSplit: str = "Split"
    phone: str = "Phone"
    gradYear: str = "Grad Year"
    newbie: str = "Newbie"
    shirt: str = "Shirt Size"
    studentId: str = "PS#"
    others: Dict[str, str] = {}

class SpreadsheetSheets():
    fullRoster: str = "Roster"
    currentRoster: str = "Current"
    others: Dict[str, str] = {}


class Glot(commands.Bot):
    glanvasURL: str = ''
    defaultURL: str = ''
    calendarId: str = ''
    defaultCalId: str = ''
    currentGuild: Guild = None
    all_roles: Sequence[Role]
    t1: str = "Tenor 1"
    t1Role: Callable[[], Role]
    t2: str = "Tenor 2"
    t2Role: Callable[[], Role]
    bari: str = "Baritone"
    bariRole: Callable[[], Role]
    bass: str = "Bass"
    bassRole: Callable[[], Role]
    tacet: str = "TACET"
    tacetRole: Callable[[], Role]
    voice_parts: Callable[[], List[Role]]
    alumni: str = "Alumni"
    alumniRole: Callable[[], Role]
    tour: str = "Tour"
    tourRole: Callable[[], Role]
    panther: str = "Pantherhythms"
    pantherRole: Callable[[], Role]
    check: str = "Nice Boi"
    checkRole: Callable[[], Role]
    board: str = "E-Board"
    boardRole: Callable[[], Role]
    roster_id: str = ''
    default_roster_id: str = ''
    rosterColumns = SpreadsheetColumns()
    rosterSheets = SpreadsheetSheets()

    def setGuild(self, guild: Guild):
        self.currentGuild = guild
        self.all_roles = self.currentGuild.roles
        self.t1Role = lambda: discord.utils.find(lambda r:r.name == self.t1, self.all_roles)
        self.t2Role = lambda: discord.utils.find(lambda r:r.name == self.t2, self.all_roles)
        self.bariRole = lambda: discord.utils.find(lambda r:r.name == self.bari, self.all_roles)
        self.bassRole = lambda: discord.utils.find(lambda r:r.name == self.bass, self.all_roles)
        self.tacetRole = lambda: discord.utils.find(lambda r:r.name == self.tacet, self.all_roles)
        self.voice_parts = lambda: [self.t1Role, self.t2Role, self.bariRole, self.bassRole, self.tacetRole]
        self.alumniRole = lambda: discord.utils.find(lambda r:r.name == self.alumni, self.all_roles)
        self.tourRole = lambda: discord.utils.find(lambda r:r.name == self.tour, self.all_roles)
        self.pantherRole = lambda: discord.utils.find(lambda r:r.name == self.panther, self.all_roles)
        self.checkRole = lambda: discord.utils.find(lambda r:r.name == self.check, self.all_roles)
        self.boardRole = lambda: discord.utils.find(lambda r:r.name == self.board, self.all_roles)
        self.voice_parts = lambda: [self.t1Role(), self.t2Role(), self.bariRole(), self.bassRole(), self.tacetRole()]
