import enum
from logging import PlaceHolder
from re import A
import discord 
from discord.ext import commands
from discord import SelectOption, app_commands
import settings
import utils
import typing
import traceback
    
logger = settings.logging.getLogger("bot")

# def is_owner():
#     def predicate(interaction : discord.Interaction):
#         if interaction.user.id == interaction.guild.owner.id:
#             return True
#     return app_commands.check(predicate)

def run():
    intents = discord.Intents.all()
    intents.message_content = True
    intents.members = True
    
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

    # cog commands
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
