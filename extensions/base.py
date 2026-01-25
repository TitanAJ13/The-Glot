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

# @commands.command(name='nicknames', help="Sends members their official glicknames for introductions")
# @commands.has_guild_permissions(administrator=True)
# async def send_nicknames(ctx: commands.Context):
#     items = [
#         { 'id': 551859223798087685,  'name': "Anthony Arshoun", 'nickname': "Afroman 2: Take to the Skies"},
#         { 'id': 555502579417743375,  'name': "Luca Assandri", 'nickname': "The Drab Strapping Kapper in a Dapper Cabbing Cap….er"},
#         { 'id': 1011054482890690712,  'name': "Luke Bailey", 'nickname': "Sauerkraut"},
#         { 'id': 543962370322595841,  'name': "Owen Bearman", 'nickname': "Afroman 3: Taking the A-Train"},
#         { 'id': 676964201692135514,  'name': "Nolan Blaze", 'nickname': "Whitney Chewston"},
#         { 'id': 711612104364392549,  'name': "Vincent Brown", 'nickname': "Season 2 Episode 25: Lord of the Beans"},
#         { 'id': 657807857374330881,  'name': "Glenn Ferry", 'nickname': "Aperol Spritzee"},
#         { 'id': 505554394675150869,  'name': "Patrick Francis", 'nickname': "Inhumane Society"},
#         { 'id': 667939229443293195,  'name': "Rory Kaplan", 'nickname': "Technically Not a Little Guy"},
#         { 'id': 456213830259703819,  'name': "Jacob Klinedinst", 'nickname': "HP OfficeJet Pro 8710 All-in-One Printer"},
#         { 'id': 584819290696450068,  'name': "Evan Knott", 'nickname': "Phantom of the Glee Club"},
#         { 'id': 381550247945699328,  'name': "Henry Leavitt", 'nickname': "Munchlax"},
#         { 'id': 1278881585705259009,  'name': "John Logue", 'nickname': "John Logue Gohn Rogue Hit the Rogue To Get His Lahn Mogued"},
#         { 'id': 594523609209241601,  'name': "Ryan O'Connor", 'nickname': "Gone Fishin'"},
#         { 'id': 519974041818497084,  'name': "Xavier Ramirez", 'nickname': "BFG (Big Fucking Glossary)"},
#         { 'id': 1139244177419403294,  'name': "Luke Sandusky", 'nickname': "Flix n' Chill"},
#         { 'id': 700130628741496922,  'name': "Jacob Shinder", 'nickname': "Fruit Puree (Grape, Peach, Orange, Strawberry and Raspberry), Corn Syrup, Sugar, Modified Corn Starch, Gelatin, Concord Grape Juice from Concentrate, Citric Acid, Lactic Acid, Natural and Artificial Flavors, Ascorbic Acid (Vitamin C), Alpha Tocopherol Acetate (Vitamin E), Vitamin A Palmitate, Sodium Citrate, Coconut Oil, Carnauba Wax, Annatto (Color), Turmeric (Color), Red 40, and Blue 1."},
#         { 'id': 1280158352839540736,  'name': "Nick Sobolewski", 'nickname': "Cookies and Cream"},
#         { 'id': 753759191717380156,  'name': "Mar Stevenson", 'nickname': "The New KFC Cheesy Zinger Triple Down Chicken Wrap #OutOfThisWorld"},
#         { 'id': 1142298406690234448,  'name': "Ethan Taylor", 'nickname': "Debt Collector"},
#         { 'id': 279070090257891339,  'name': "Natividad Torres", 'nickname': "Bob Ross Chia Pet"},
#         { 'id': 695797312772898861,  'name': "Ian Whitaker", 'nickname': "Hannibal Barca (conquerer of the alps, rider of elephants, led Carthage to many victories, silver collector, and slayer of Romans)"}
#     ]

#     for item in items:
#         user = discord.Object(item['id'])
#         print(f"UserID: {item['id']}, User: {user}")
#         await user.send(f"Hey there {item['name']}! Here's your glickname for intros today in case you forgot.\n\n**This is your only nickname and there are no fake nicknames. Please don't mention fake nicknames to the newbies.**\n\nGlickname: `{item['nickname']}`")
#         print(f'Sent a message to {item['name']}')

async def setup(bot: Glot):
    bot.add_command(post_events)