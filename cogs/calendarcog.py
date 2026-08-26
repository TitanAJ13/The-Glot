import discord
from discord import app_commands
from discord.ext import commands
from glot import Glot
import authenticate
from googleapiclient.errors import HttpError
from typing import Literal, Optional, Dict
import datetime
from zoneinfo import ZoneInfo
import re

class CalendarCog(commands.Cog):
    def __init__(self, bot: Glot):
        self.bot = bot
        self.sync_token = ''
        sync_command = app_commands.Command(
            name="sync-calendar",
            callback= self.sync_calendar,
            guild_ids=[bot.currentGuild.id],
            description="Sync events from the PMGC Google Calendar"
        )
        bot.tree.add_command(sync_command, guild=bot.currentGuild)

    @app_commands.checks.has_permissions(administrator=True)
    async def sync_calendar(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

        options = {
            'calendarId': self.bot.calendarId,
            'timeMin': now,
            'singleEvents': True
        }

        if self.sync_token != '':
            options['syncToken'] = self.sync_token
            del options['timeMin']

        edit_count = 0
        add_count = 0
        del_count = 0

        discord_list = await interaction.guild.fetch_scheduled_events()
        id_dict: Dict[str, discord.ScheduledEvent] = {}

        for event in discord_list:
            desc = event.description
            if desc:
                id = re.search(r'\|\|\[.+?\].+?#(.+?)(?=>\)\|\|\Z)', desc)
                if id:
                    id_dict[id.group(1)] = event

        service = authenticate.callService("calendar", "v3")

        offset = datetime.datetime.now(ZoneInfo('America/New_York')).strftime('%:z')

        google_dict = {}

        while True:
            try:
                result = (
                    service.events().list(**options)
                    .execute()
                )
            except HttpError as e:
                if e.status_code == 410:
                    #Stale sync token, needs to full sync again
                    self.sync_token = ''
                    del options['syncToken']
                    options['timeMin'] = now
                    result = (
                        service.events().list(**options)
                        .execute()
                    )
                else:
                    raise e
            
            event_list = result.get('items', [])

            for event in event_list:
                status = event.get('status', 'confirmed')
                title = event.get('summary', 'Untitled Event')
                description = event.get('description', '')
                location = event.get('location', '')
                start = datetime.datetime.fromisoformat(event['start'].get('dateTime') or event['start'].get('date') + 'T00:00:00' + offset) if status != 'cancelled' else ''
                end = datetime.datetime.fromisoformat(event['end'].get('dateTime') or event['end'].get('date') + 'T23:59:59' + offset) if status != 'cancelled' else ''

                id = event.get('id')
                google_dict[id] = event

                if id in id_dict:
                    #Event exists already, so modify or delete it if necessary
                    devent = id_dict[id]
                    if status == 'cancelled':
                        await devent.delete()
                        del_count = del_count + 1
                        await interaction.edit_original_response(content=f"New Events Synced: `{add_count}`\nExisting Events Modified: `{edit_count}`\nStale Events Deleted: `{del_count}`\n\n*Loading More...*")
                    else:
                        recreate = False
                        edits = {}
                        if (devent.name != title):
                            edits['name'] = title
                        if (devent.description != description + f'\u200b\n \n \n \n \n-# ||[‍𓏺](<https://calendar.google.com/calendar/embed?src={self.bot.calendarId}&ctz=America%2FNew_York#{id}>)||'):
                            edits['description'] = description + f'\u200b\n \n \n \n \n-# ||[‍𓏺](<https://calendar.google.com/calendar/embed?src={self.bot.calendarId}&ctz=America%2FNew_York#{id}>)||'
                        if (devent.location != location):
                            edits['location'] = location

                        dtnow = datetime.datetime.now(ZoneInfo('America/New_York'))
                        if (devent.start_time != start):
                            if start < dtnow:
                                edits['status'] = discord.EventStatus.active
                            elif devent.status == discord.EventStatus.active:
                                # There is no way to change an active event to inactive. We must delete and recreate
                                edits['status'] = discord.EventStatus.completed
                                recreate = True
                            else:
                                edits['start_time'] = start
                        if (devent.end_time != end):
                            if end < dtnow:
                                edits['status'] = discord.EventStatus.completed if (devent.status in [discord.EventStatus.active, discord.EventStatus.completed]) else discord.EventStatus.cancelled
                                recreate = False
                                del_count = del_count + 1
                                edit_count = edit_count - 1
                            elif edits.get('status') not in [discord.EventStatus.completed]:
                                edits['end_time'] = end

                        split_steps = False
                        if end < devent.start_time and edits.get('status') in [discord.EventStatus.active]:
                            split_steps = True
                            edits['start_time'] = end - datetime.timedelta(minutes=1)
                            del edits['status']

                        if len(edits) > 0:
                            edits['reason'] = 'Calendar Sync'
                            edits['entity_type'] = discord.EntityType.external
                            edits['privacy_level'] = discord.PrivacyLevel.guild_only
                            devent = await devent.edit(**edits)
                            if (split_steps):
                                await devent.edit(status= discord.EventStatus.active)
                            edit_count = edit_count + 1
                            await interaction.edit_original_response(content=f"New Events Synced: `{add_count}`\nExisting Events Modified: `{edit_count}`\nStale Events Deleted: `{del_count}`\n\n*Loading More...*")

                        if (recreate):
                            props = {
                                'name': title,
                                'description': description + f'\u200b\n \n \n \n \n-# ||[‍𓏺](<https://calendar.google.com/calendar/embed?src={self.bot.calendarId}&ctz=America%2FNew_York#{id}>)||',
                                'location': location,
                                'start_time': start,
                                'end_time': end,
                                'reason': 'Calendar Sync',
                                'entity_type': discord.EntityType.external,
                                'privacy_level': discord.PrivacyLevel.guild_only
                            }
                            await interaction.guild.create_scheduled_event(**props)
                else:
                    if status == 'cancelled': continue
                    dtnow = datetime.datetime.now(ZoneInfo('America/New_York'))
                    if end < dtnow: continue
                    setActive = False
                    if start < dtnow:
                        start = dtnow + datetime.timedelta(minutes=2) # give a buffer time for network delay
                        setActive = True

                    #Event doesn't exist, so create it
                    props = {
                        'name': title,
                        'description': description + f'\u200b\n \n \n \n \n-# ||[‍𓏺](<https://calendar.google.com/calendar/embed?src={self.bot.calendarId}&ctz=America%2FNew_York#{id}>)||',
                        'location': location,
                        'start_time': start,
                        'end_time': end,
                        'reason': 'Calendar Sync',
                        'entity_type': discord.EntityType.external,
                        'privacy_level': discord.PrivacyLevel.guild_only
                    }
                    ev = await interaction.guild.create_scheduled_event(**props)
                    if (setActive):
                        await ev.start()
                    add_count = add_count + 1
                    await interaction.edit_original_response(content=f"New Events Synced: `{add_count}`\nExisting Events Modified: `{edit_count}`\nStale Events Deleted: `{del_count}`\n\n*Loading More...*")


            nextpage = result.get('nextPageToken', '')
            if nextpage != '':
                options['pageToken'] = nextpage
            else:
                break

        # Backup when no sync token
        if self.sync_token == '':
            for gid, d_event in id_dict.items():
                if gid not in google_dict:
                    # Google event was cancelled/deleted -> Delete corresponding discord event
                    await d_event.delete()
                    del_count = del_count + 1
                    await interaction.edit_original_response(content=f"New Events Synced: `{add_count}`\nExisting Events Modified: `{edit_count}`\nStale Events Deleted: `{del_count}`\n\n*Loading More...*")

        self.sync_token = result.get('nextSyncToken', '')
        await interaction.edit_original_response(content=f"New Events Synced: `{add_count}`\nExisting Events Modified: `{edit_count}`\nStale Events Deleted: `{del_count}`\n\n*All Done!*")


async def setup(bot: Glot):
    await bot.add_cog(CalendarCog(bot), guild=bot.currentGuild)