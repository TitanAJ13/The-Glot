import discord
from discord.ext import commands
import datetime
from glot import Glot
from zoneinfo import ZoneInfo

@commands.command(name="calendar",help="Loads the calendar into Discord Events")
@commands.has_guild_permissions(administrator=True)
async def post_events(ctx: commands.Context):
    times = [
        "1/14/2026 7:30pm",
        "1/16/2026 5:00pm",
        "1/18/2026 6:00pm",
        "1/21/2026 7:30pm",
        "1/23/2026 5:00pm",
        "1/25/2026 6:00pm",
        "1/28/2026 7:30pm",
        "2/1/2026 6:00pm",
        "2/4/2026 7:30pm",
        "2/7/2026 10:00am",
        "2/7/2026 2:30pm",
        "2/11/2026 7:30pm",
        "2/13/2026 5:00pm",
        "2/15/2026 6:00pm",
        "2/18/2026 7:30pm",
        "2/22/2026 6:00pm",
        "2/25/2026 7:30pm",
        "3/1/2026 6:00pm",
        "3/4/2026 7:30pm",
        "3/18/2026 7:30pm",
        "3/22/2026 6:00pm",
        "3/25/2026 7:30pm",
        "3/29/2026 6:00pm",
        "4/1/2026 7:30pm",
        "4/8/2026 7:30pm",
        "4/12/2026 6:00pm"
    ]
    count = 0
    failures = []
    for i in range(len(times)):
        item = times[i]
        try:
            temp = item.split(" ")
            date = temp[0].split("/")
            month = int(date[0])
            day = int(date[1])
            year = int(date[2])
            time = temp[1].split(":")
            hour = int(time[0])
            minute = time[1]
            if (minute.endswith("pm")):
                hour = hour + 12
            minute = int(minute[:-2])

            start = datetime.datetime.now().astimezone(ZoneInfo("America/New_York"))
            start = start.replace(year, month, day, hour, minute)
            print(start)
            end = start + datetime.timedelta(hours=2)
            await ctx.guild.create_scheduled_event(
                name="Rehearsal",
                location="Frick Fine Arts Auditorium (Rm 125)",
                reason="Google Calendar",
                start_time=start,
                end_time=end,
                entity_type=discord.EntityType.external,
                privacy_level=discord.PrivacyLevel.guild_only,
                description="")
            count = count + 1
        except:
            failures.append(i)
        
    await ctx.reply(f"Successfully added {count} events!\n\n{'There were no errors!' if len(failures) == 0 else f"Errors occured at the following indices:\n{failures}"}")

async def setup(bot: Glot):
    bot.add_command(post_events)