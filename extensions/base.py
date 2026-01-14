import discord
from discord.ext import commands
import datetime
from glot import Glot

@commands.command(name="calendar",help="Loads the calendar into Discord Events")
@commands.has_guild_permissions(administrator=True)
async def post_events(ctx: commands.Context):
    datetime.datetime.fromisoformat("")
    await ctx.guild.create_scheduled_event(name="Rehearsal",location="Frick Auditorium (Rm 125)")

@commands.command(name='nicknames', help="Sends members their official glicknames for introductions")
@commands.has_guild_permissions(administrator=True)
async def send_nicknames(ctx: commands.Context):
    items = [
        { 'id': 551859223798087685,  'name': "Anthony Arshoun", 'nickname': "Afroman 2: Take to the Skies"},
        { 'id': 555502579417743375,  'name': "Luca Assandri", 'nickname': "The Drab Strapping Kapper in a Dapper Cabbing Cap….er"},
        { 'id': 1011054482890690712,  'name': "Luke Bailey", 'nickname': "Sauerkraut"},
        { 'id': 543962370322595841,  'name': "Owen Bearman", 'nickname': "Afroman 3: Taking the A-Train"},
        { 'id': 676964201692135514,  'name': "Nolan Blaze", 'nickname': "Whitney Chewston"},
        { 'id': 711612104364392549,  'name': "Vincent Brown", 'nickname': "Season 2 Episode 25: Lord of the Beans"},
        { 'id': 657807857374330881,  'name': "Glenn Ferry", 'nickname': "Aperol Spritzee"},
        { 'id': 505554394675150869,  'name': "Patrick Francis", 'nickname': "Inhumane Society"},
        { 'id': 667939229443293195,  'name': "Rory Kaplan", 'nickname': "Technically Not a Little Guy"},
        { 'id': 456213830259703819,  'name': "Jacob Klinedinst", 'nickname': "HP OfficeJet Pro 8710 All-in-One Printer"},
        { 'id': 584819290696450068,  'name': "Evan Knott", 'nickname': "Phantom of the Glee Club"},
        { 'id': 381550247945699328,  'name': "Henry Leavitt", 'nickname': "Munchlax"},
        { 'id': 1278881585705259009,  'name': "John Logue", 'nickname': "John Logue Gohn Rogue Hit the Rogue To Get His Lahn Mogued"},
        { 'id': 594523609209241601,  'name': "Ryan O'Connor", 'nickname': "Gone Fishin'"},
        { 'id': 519974041818497084,  'name': "Xavier Ramirez", 'nickname': "BFG (Big Fucking Glossary)"},
        { 'id': 1139244177419403294,  'name': "Luke Sandusky", 'nickname': "Flix n' Chill"},
        { 'id': 700130628741496922,  'name': "Jacob Shinder", 'nickname': "Fruit Puree (Grape, Peach, Orange, Strawberry and Raspberry), Corn Syrup, Sugar, Modified Corn Starch, Gelatin, Concord Grape Juice from Concentrate, Citric Acid, Lactic Acid, Natural and Artificial Flavors, Ascorbic Acid (Vitamin C), Alpha Tocopherol Acetate (Vitamin E), Vitamin A Palmitate, Sodium Citrate, Coconut Oil, Carnauba Wax, Annatto (Color), Turmeric (Color), Red 40, and Blue 1."},
        { 'id': 1280158352839540736,  'name': "Nick Sobolewski", 'nickname': "Cookies and Cream"},
        { 'id': 753759191717380156,  'name': "Mar Stevenson", 'nickname': "The New KFC Cheesy Zinger Triple Down Chicken Wrap #OutOfThisWorld"},
        { 'id': 1142298406690234448,  'name': "Ethan Taylor", 'nickname': "Debt Collector"},
        { 'id': 279070090257891339,  'name': "Natividad Torres", 'nickname': "Bob Ross Chia Pet"},
        { 'id': 695797312772898861,  'name': "Ian Whitaker", 'nickname': "Hannibal Barca (conquerer of the alps, rider of elephants, led Carthage to many victories, silver collector, and slayer of Romans)"}
    ]

    for item in items:
        user = discord.Object(item['id'])
        print(f"UserID: {item['id']}, User: {user}")
        await user.send(f"Hey there {item['name']}! Here's your glickname for intros today in case you forgot.\n\n**This is your only nickname and there are no fake nicknames. Please don't mention fake nicknames to the newbies.**\n\nGlickname: `{item['nickname']}`")
        print(f'Sent a message to {item['name']}')

async def setup(bot: Glot):
    pass