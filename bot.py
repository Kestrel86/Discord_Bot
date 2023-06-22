from re import A
import enum
import discord
import settings
import random
from discord.ext import commands
from discord import app_commands
import utils

logger = settings.logging.getLogger("bot")

# def is_certain_user():
#     def predicate(interaction : discord.Interaction):
#         if interaction.user.id == "_Uptown":
#             return True
#     return app_commands.check(predicate)

def run():
    intents = discord.Intents.all()
    intents.members = True
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event 
    async def on_ready():
        #logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
        #logger.info(f"Guild Id: {bot.guilds[0].id}")   

        await bot.load_extension("cmds.debug")

        for cog_file in settings.COGS_DIR.glob("*.py"):
            if cog_file.name != "__init__.py":
                await bot.load_extension(f"cogs.{cog_file.name[:-3]}")

        # for slashcmd_file in settings.SLASH_DIR.glob("*.py"):
        #     if slashcmd_file.name != "__init__.py":
        #         await bot.load_extension(f"slashcmds.{slashcmd_file.name[:-3]}")

        bot.tree.copy_global_to(guild=settings.GUILDS_ID)
        await bot.tree.sync(guild=settings.GUILDS_ID)
        await utils.load_videocmds(bot)

    @bot.command()
    async def load(ctx, cog: str):
        await bot.load_extension(f"cogs.{cog.lower()}")
        
    @bot.command()
    async def unload(ctx, cog: str):
        await bot.unload_extension(f"cogs.{cog.lower()}")
        
    @bot.command()
    async def reload(ctx, cog: str):
        await bot.reload_extension(f"cogs.{cog.lower()}")

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
