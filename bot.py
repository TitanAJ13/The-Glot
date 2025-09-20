import os
# from typing import Any, Literal, Optional
import discord
from discord.ext import commands
from discord import app_commands, ui
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import fitz
from datetime import date, datetime, timezone
from io import BytesIO
from cogs.linkcog import LinkCog
from cogs.filecog import FileCog
from cogs.itemcog import ItemCog
from cogs.modulecog import ModuleCog
from cogs.musiccog import MusicCog
from cogs.announcementcog import AnnouncementCog
# import requests
# import re
# import markdown
# from extensions import StrikethroughExtension

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot_intents = discord.Intents.all()
bot_intents.message_content = True
bot_intents.guilds = True
bot_intents.guild_messages = True
bot_intents.members = True
bot = commands.Bot(command_prefix = '!', intents=bot_intents)

data = None
all_roles = None
t1 = None
t2 = None
bari = None
bass = None
tacet = None
alumni = None
guildPMGC = None
guildTest = None

# @client.event
@bot.event
async def on_ready():
    global data
    try:
        data = pd.read_excel("H:/My Drive/The Google Glive/Fall 2025 Roster.xlsx",sheet_name="Roster", usecols=[0,1,2,4,6,7,13], index_col=2)
        data.index = data.index.str.lower()
    except Exception as e:
        print(f'Roster could not be loaded: {e}')

    global all_roles
    all_roles = discord.utils.find(lambda g:g.name == "Pitt Men's Glee Club", bot.guilds).roles
    # all_roles = client.guilds[0].roles

    global t1
    global t2
    global bari
    global bass
    global tacet
    global alumni
    global guildPMGC
    global guildTest
    t1 = discord.utils.find(lambda r:r.name == "Tenor 1", all_roles)
    t2 = discord.utils.find(lambda r:r.name == "Tenor 2", all_roles)
    bari = discord.utils.find(lambda r:r.name == "Baritone", all_roles)
    bass = discord.utils.find(lambda r:r.name == "Bass", all_roles)
    tacet = discord.utils.find(lambda r:r.name == "TACET", all_roles)
    alumni = discord.utils.find(lambda r:r.name == "Alumni", all_roles)
    guildPMGC = bot.get_guild(614104404102086658)
    guildTest = bot.get_guild(1378895395253387344)

    bot.tree.clear_commands(guild=None)

    # cogfiles = [
    #     # 'linkcog',
    #     # 'filecog',
    #     # 'musiccog',
    #     # 'modulecog',
    #     # 'itemcog',
    #     'announcementcog'
    #     ]
    # for i in range(len(cogfiles)):
    #     await bot.load_extension(f'cogs.{cogfiles[i]}', base='http://127.0.0.1:5000/')
    # await bot.add_cog(LinkCog(bot,'http://127.0.0.1:5000/'), guild=guildTest)
    # await bot.add_cog(FileCog(bot,'http://127.0.0.1:5000/'), guild=guildTest)
    # await bot.add_cog(ItemCog(bot,'http://127.0.0.1:5000/'), guild=guildTest)
    # await bot.add_cog(ModuleCog(bot,'http://127.0.0.1:5000/'), guild=guildTest)
    # await bot.add_cog(MusicCog(bot,'http://127.0.0.1:5000/'), guild=guildTest)
    await bot.add_cog(AnnouncementCog(bot,'https://aja138.pythonanywhere.com/'), guild=guildPMGC)
    # await bot.add_cog(MyCog(bot), guild=guildTest)

    print("Loaded Cogs!")

    print("Synced the following commands:\n", await bot.tree.sync(guild=guildPMGC))
    print("Connected to the Guild!")

# @bot.tree.context_menu(name="Test Menu")
# @app_commands.guilds(1378895395253387344)
# async def react(interaction: discord.Interaction, message: discord.Message):
#     await interaction.response.send_message('Very cool message!', ephemeral=True)

# Command to sync application commands
@bot.command(name='sync')
@commands.is_owner() # Optional: Restrict to bot owner
async def sync(ctx):
    globalResults = await bot.tree.sync(guild=None)
    guildResults = await bot.tree.sync(guild=discord.Object(1378895395253387344))
    await ctx.send(f"Synced the following global commands: {globalResults}\nSynced the following guild commands: {guildResults}")

# Command to sync application commands
@bot.command(name='clear')
@commands.is_owner() # Optional: Restrict to bot owner
async def clear(ctx):
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync(guild=None)
    await ctx.send(f"Cleared commands")


''' Command syntax:

/glanvas link|module|announcement all|

/glanvas add|delete|clear link|module -> UI

/glanvas add link|module -> UI
/glanvas delete link|module|announcement?
/
'''

# bot.create

# @bot.tree.command(name="test",description="Redesigned")
# # @app_commands.describe(member='The member to select', channel='The text-channel to select')
# async def preview_command(interaction: discord.Interaction):
#     embed = {
#         "title": "Test Embed",
#         "type": "rich",
#         "color": 0x0000ee
#     }
#     await interaction.response.send_message(f"Test command ran",embed=discord.Embed.from_dict(embed))
#     interaction.
    

# @client.event
@bot.event
async def on_message(message: discord.Message):
    # if message.guild.name != "Bot Testing": return

    if message.author == bot.user: return
    # if message.author == client.user: return

    if isinstance(message.channel, discord.DMChannel):
        dm = bot.get_channel(1414317415751356587)
        message.forward(dm)
        return
    # if message.channel.id != 1373362239532302399: return
    channel = message.channel.name
    if channel == "verifications":
        await normal_verify(message)
        return
    elif channel == "posted-announcements":
        await post_announcement(message)
        return
    elif channel == "bot-commands":
        await bot.process_commands(message)
        return
    attachments = filter(lambda a: a.content_type == "application/pdf", message.attachments)
    if (attachments):
        for a in attachments:
            await file_preview(message, a)



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

async def post_announcement(message: discord.Message):
    pass

async def normal_verify(message: discord.Message):
    user = message.author
    id = user.id
    email = message.content.strip().lower()

    check = discord.utils.find(lambda r: r.name == "Nice Boi", all_roles)
    if check not in user.roles:
        if not email.endswith('@pitt.edu'):
            email = f'{email}@pitt.edu'

        entry = data.loc[email]

        id = entry.get("Discord ID")
        if (not np.isnan(id)):
            await message.reply("Sorry, that email has already been used to verify another member")
        else:
            first = entry.get("First Name")
            last = entry.get("Last Name")
            section = entry.get("Voice Part")
            inactive = entry.get("Tacet") == "TRUE"
            year = entry.get("Year")

            section_role = discord.utils.find(lambda r: r.name == section, all_roles)
            # print(f"Role type: {section_role}")

            roles = user.roles

            # Remove Incorrect Roles

            if (t1 in roles and (t1 != section_role or inactive)):
                print("removing t1")
                await user.remove_roles(t1,reason="Verification")
            if (t2 in roles and (t2 != section_role or inactive)):
                print("removing t2")
                await user.remove_roles(t2,reason="Verification")
            if (bari in roles and (bari != section_role or inactive)):
                print("removing bari")
                await user.remove_roles(bari,reason="Verification")
            if (bass in roles and (bass != section_role or inactive)):
                print("removing bass")
                await user.remove_roles(bass,reason="Verification")

            # Add Correct Roles
            await user.add_roles(check,tacet if inactive else section_role,reason="Verification")
            if (year == "Alumni" and alumni not in roles):
                await user.add_roles(alumni, reason="Verification")

            # Edit Server Nickname
            await user.edit(nick=f"{first} {last}")

            # Respond to message
            await message.reply("Verification completed! Welcome to the Glee Club! <:glee:1077812002107424879>")

@bot.command(name='preview', help='Generate file preview for a previously sent message')
@commands.has_guild_permissions(administrator=True)
async def force_preview(ctx: commands.Context, channelId:int, messageId: int):
    message = await bot.get_channel(channelId).fetch_message(messageId)

    attachments = filter(lambda a: a.content_type == "application/pdf", message.attachments)
    if (attachments):
        for a in attachments:
            await file_preview(message, a)

@bot.command(name='ids', help="Prints out a list of members and their ids for later use")
@commands.has_guild_permissions(administrator=True)
async def print_ids(ctx: commands.Context):
    members = list(guildPMGC.members)

    members.sort(key= lambda member: " ".join([" ".join(member.display_name.split(" ")[1:]),member.display_name.split(" ")[0]]))

    for member in members:
        print(f'{member.display_name}\t{member.id}')


@bot.command(name="calendar",help="Loads the calendar into Discord Events")
@commands.has_guild_permissions(administrator=True)
async def post_events(ctx: commands.Context):
    datetime.datetime.fromisoformat("")
    await ctx.guild.create_scheduled_event(name="Rehearsal",location="Frick Auditorium (Rm 125)")

@bot.command(name='nicknames', help="Sends members their official glicknames for introductions")
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
        user = bot.get_user(item['id'])
        print(f"UserID: {item['id']}, User: {user}")
        await user.send(f"Hey there {item['name']}! Here's your glickname for intros today in case you forgot.\n\n**This is your only nickname and there are no fake nicknames. Please don't mention fake nicknames to the newbies.**\n\nGlickname: `{item['nickname']}`")
        print(f'Sent a message to {item['name']}')

@bot.command(name='verify', help="Verifies new members")
@commands.has_guild_permissions(administrator=True)
async def verify_admin(ctx : commands.Context, id: int, email : str):
    print("Command run")

    user = discord.utils.find(lambda u:u.id == id, ctx.guild.members)

    if ctx.channel.id != 1373362239532302399: return
    email = email.strip().lower()

    check = discord.utils.find(lambda r: r.name == "Nice Boi", all_roles)
    if check not in user.roles:
        if not email.endswith('@pitt.edu'):
            email = f'{email}@pitt.edu'

        entry = data.loc[email]
        # print("Found email")
        first = entry.get("First Name")
        # print("Found first name")
        last = entry.get("Last Name")
        # print("Found last name")
        section = entry.get("Voice Part").split(" (")[0]
        # print("Found voice part")

        role = discord.utils.find(lambda r:r.name == section, all_roles)
        print(f"Role type: {role}")

        roles = user.roles

        if (t1 in roles and t1 != role):
            print("removing t1")
            await user.remove_roles(t1,reason="Verification")
        if (t2 in roles and t2 != role):
            print("removing t2")
            await user.remove_roles(t2,reason="Verification")
        if (bari in roles and bari != role):
            print("removing bari")
            await user.remove_roles(bari,reason="Verification")
        if (bass in roles and bass != role):
            print("removing bass")
            await user.remove_roles(bass,reason="Verification")

        print("Adding roles")
        await user.add_roles(check,role,reason="Verification")

        print("editting nickname")
        await user.edit(nick=f"{first} {last}")

        await ctx.reply("Verification completed! Welcome to the Glee Club! <:glee:1077812002107424879>")
        # try:
        # except:
        #     await ctx.reply("Sorry, that email wasn't found in my system. Please check for typos or wait a few days for admins to update the system.")

@bot.event
async def on_command_error(ctx, error : commands.CommandError):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.reply("Sorry, you don't have permission to run that command")
    elif isinstance(error, commands.errors.TooManyArguments):
        await ctx.reply("ERROR: Too many arguments; I don't know what to do with this")
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.reply(f"ERROR: Missing required argument `{error.param}`")
    else:
        await ctx.reply(f"{error}")

bot.run(TOKEN)