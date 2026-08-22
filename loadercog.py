import discord
from discord.ext import commands
from discord import app_commands
from glot import Glot
import os

class CogLoaderCog(commands.Cog):
    group = app_commands.Group(name="cog", description="Work with the dynamically-loaded cogs")

    def __init__(self, bot: Glot) -> None:
        self.bot = bot
        self.group._guild_ids = [bot.currentGuild.id]

    @group.command(name="list", description="Lists all detected cogs and their states")
    async def cog_list(self, interaction: discord.Interaction):
        all_extensions = self.bot.extensions
        loaded = []
        for item in all_extensions.keys():
            if not item.startswith("cogs."): continue
            loaded.append(item[5:])

        active = []
        inactive = []
        for filename in os.listdir("cogs"):
            if (filename.endswith("cog.py")):
                cog = all_extensions.get(f'cogs.{filename[:-3]}')
                if cog:
                    active.append(filename[:-3])
                else:
                    inactive.append(filename[:-3])

        unstable = []
        for item in loaded:
            if item not in active:
                unstable.append(item)

        message = ""
        if (len(active) > 0):
            message = message + "Active Cogs:"
            for item in active:
                message = message + f"\n* {item}"
        else:
            message = message + "No Active Cogs"

        if (len(inactive) > 0):
            message = message + "\n\nInactive Cogs:"
            for item in inactive:
                message = message + f"\n* {item}"
        else:
            message = message + "\n\nNo Inactive Cogs"

        if (len(unstable) > 0):
            message = message + "\n\nUnstable Cogs:"
            for item in unstable:
                message = message + f"\n* {item}"
        else:
            message = message + "\n\nNo Unstable Cogs"

        await interaction.response.send_message(message)

    @group.command(name="load", description="Loads a new cog")
    @app_commands.describe(name="The filename of the cog to load")
    async def mycog_load(self, interaction: discord.Interaction, name:str):
        if (name == ''):
            await interaction.response.send_message('ERROR: `name` cannot be empty')

        if (name.endswith('.py')):
            name = name[:-3]

        if (name.startswith('cogs.')):
            name = name[5:]

        if (not name.endswith('cog')):
            name = name + 'cog'

        try:
            await self.bot.load_extension(f'cogs.{name}')
            await self.bot.tree.sync(guild=self.bot.currentGuild)
            await interaction.response.send_message(f"Successfully loaded Cog `{name}`!")
        except commands.ExtensionAlreadyLoaded:
            await interaction.response.send_message(f'ERROR: Cog `{name}` is already loaded')
        except commands.ExtensionNotFound:
            await interaction.response.send_message(f'ERROR: Cog `{name}` not found in the `cogs` directory')
        except Exception as e:
            await interaction.response.send_message(f'Could not load cog `{name}` — {e}')

    @group.command(name="reload", description="Reloads a cog")
    @app_commands.describe(name="The filename of the cog to reload")
    async def mycog_reload(self, interaction: discord.Interaction, name:str):
        if (name == ''):
            await interaction.response.send_message('ERROR: `name` cannot be empty')

        if (name.endswith('.py')):
            name = name[:-3]

        if (name.startswith('cogs.')):
            name = name[5:]

        if (not name.endswith('cog')):
            name = name + 'cog'

        try:
            await self.bot.reload_extension(f'cogs.{name}')
            await self.bot.tree.sync(guild=self.bot.currentGuild)
            await interaction.response.send_message(f"Successfully reloaded Cog `{name}`!")
        except commands.ExtensionNotLoaded:
            await interaction.response.send_message(f'ERROR: Cog `{name}` has not been loaded yet')
        except commands.ExtensionNotFound:
            await interaction.response.send_message(f'ERROR: Cog `{name}` not found in the `cogs` directory')
        except Exception as e:
            await interaction.response.send_message(f'Could not reload cog `{name}` — {e}')

    @group.command(name="refresh", description="Loads/Reloads all the cogs in the `cogs` directory")
    async def cog_refresh(self, interaction: discord.Interaction):
        success = []
        failure = []
        for filename in os.listdir("cogs"):
            if (filename.endswith("cog.py")):
                try:
                    await self.bot.reload_extension(f'cogs.{filename[:-3]}')
                    success.append(filename)
                except commands.ExtensionNotLoaded:
                    try:
                        await self.bot.load_extension(f'cogs.{filename[:-3]}')
                        success.append(filename)
                    except Exception as e:
                        failure.append((filename,e))
                except Exception as e:
                    failure.append((filename,e))

        result = ""
        if (len(success) > 0):
            result = result + "Successfully Reloaded:"
            for file in success:
                result = result + f"\n* {file}"
        else:
            result = result + "No cogs successfully Reloaded..."

        if (len(failure) > 0):
            result = result + "\n\nFailed to Reload:"
            for (file, error) in failure:
                result = result + f"\n* {file} - {error}"
        else:
            result = result + "\n\nNo Failures!"


        try:
            await self.bot.tree.sync(guild=self.bot.currentGuild)
            await interaction.response.send_message(result)
        except Exception as e:
            await interaction.response.send_message(f"ERROR: {e}")

class ExtLoaderCog(commands.Cog):
    group = app_commands.Group(name="extension", description="Work with the dynamically-loaded extensions")

    def __init__(self, bot: Glot):
        self.bot = bot
        self.group._guild_ids = [bot.currentGuild.id]

    @group.command(name="list", description="Lists all detected extensions and their states")
    async def ext_list(self, interaction: discord.Interaction):
        all_extensions = self.bot.extensions
        loaded = []
        for item in all_extensions.keys():
            if not item.startswith("extensions."): continue
            loaded.append(item[11:])

        active = []
        inactive = []
        for filename in os.listdir("extensions"):
            if (filename.endswith(".py")):
                cog = all_extensions.get(f'extensions.{filename[:-3]}')
                if cog:
                    active.append(filename[:-3])
                else:
                    inactive.append(filename[:-3])

        unstable = []
        for item in loaded:
            if item not in active:
                unstable.append(item)

        message = ""
        if (len(active) > 0):
            message = message + "Active Extensions:"
            for item in active:
                message = message + f"\n* {item}"
        else:
            message = message + "No Active Extensions"

        if (len(inactive) > 0):
            message = message + "\n\nInactive Extensions:"
            for item in inactive:
                message = message + f"\n* {item}"
        else:
            message = message + "\n\nNo Inactive Extensions"

        if (len(unstable) > 0):
            message = message + "\n\nUnstable Extensions:"
            for item in unstable:
                message = message + f"\n* {item}"
        else:
            message = message + "\n\nNo Unstable Extensions"

        await interaction.response.send_message(message)

    @group.command(name="load", description="Loads a new extension")
    @app_commands.describe(name="The filename of the extension to load")
    async def ext_load(self, interaction: discord.Interaction, name:str):
        if (name == ''):
            await interaction.response.send_message('ERROR: `name` cannot be empty')

        if (name.endswith('.py')):
            name = name[:-3]

        if (name.startswith('extensions.')):
            name = name[11:]

        try:
            await self.bot.load_extension(f'extensions.{name}')
            await self.bot.tree.sync(guild=self.bot.currentGuild)
            await interaction.response.send_message(f"Successfully loaded Extension `{name}`!")
        except commands.ExtensionAlreadyLoaded:
            await interaction.response.send_message(f'ERROR: Extension `{name}` is already loaded')
        except commands.ExtensionNotFound:
            await interaction.response.send_message(f'ERROR: Extension `{name}` not found in the `extensions` directory')
        except Exception as e:
            await interaction.response.send_message(f'Could not load extension `{name}` — {e}')

    @group.command(name="reload", description="Reloads an extension")
    @app_commands.describe(name="The filename of the extension to reload")
    async def ext_reload(self, interaction: discord.Interaction, name:str):
        if (name == ''):
            await interaction.response.send_message('ERROR: `name` cannot be empty')

        if (name.endswith('.py')):
            name = name[:-3]

        if (name.startswith('extensions.')):
            name = name[11:]

        try:
            await self.bot.reload_extension(f'extensions.{name}')
            await self.bot.tree.sync(guild=self.bot.currentGuild)
            await interaction.response.send_message(f"Successfully reloaded Extension `{name}`!")
        except commands.ExtensionNotLoaded:
            await interaction.response.send_message(f'ERROR: Extension `{name}` has not been loaded yet')
        except commands.ExtensionNotFound:
            await interaction.response.send_message(f'ERROR: Extension `{name}` not found in the `extension` directory')
        except Exception as e:
            await interaction.response.send_message(f'Could not reload extension `{name}` — {e}')

    @group.command(name="refresh", description="Loads/Reloads all the extensions in the `extensions` directory")
    async def ext_refresh(self, interaction: discord.Interaction):
        success = []
        failure = []
        for filename in os.listdir("extensions"):
            if (filename.endswith(".py")):
                try:
                    await self.bot.reload_extension(f'extensions.{filename[:-3]}')
                    success.append(filename)
                except commands.ExtensionNotLoaded:
                    try:
                        await self.bot.load_extension(f'extensions.{filename[:-3]}')
                        success.append(filename)
                    except Exception as e:
                        failure.append((filename,e))
                except Exception as e:
                    failure.append((filename,e))

        result = ""
        if (len(success) > 0):
            result = result + "Successfully Reloaded:"
            for file in success:
                result = result + f"\n* {file}"
        else:
            result = result + "No extensions successfully Reloaded..."

        if (len(failure) > 0):
            result = result + "\n\nFailed to Reload:"
            for (file, error) in failure:
                result = result + f"\n* {file} - {error}"
        else:
            result = result + "\n\nNo Failures!"

        
        try:
            await self.bot.tree.sync(guild=self.bot.currentGuild)
            await interaction.response.send_message(result)
        except Exception as e:
            await interaction.response.send_message(f"ERROR: {e}")

async def setup(bot: Glot):
    await bot.add_cog(CogLoaderCog(bot), guild=bot.currentGuild)
    await bot.add_cog(ExtLoaderCog(bot), guild=bot.currentGuild)