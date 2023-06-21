import discord
from discord.ext import commands 
import settings 
import wavelink

logger = settings.logging.getLogger(__name__)

class SB_Button(discord.ui.Button):
    file_name : str = None

    def setup(self, data):
        self.label = data["label"]
        self.custom_id = data["custom_id"]
        self.file_name = data["file_name"]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        soundboardItem = await wavelink.YouTubeTrack.search(query=self.file_name, return_first=True)
        if soundboardItem:
            await self.view.player.play(soundboardItem)

class SoundboardView(discord.ui.View):
    player : wavelink.Player = None

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red)
    async def stop_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.player.stop()

    def setupButtons(self):
        #only 25 buttons total, 24 if stop button included
        buttons = [
            {
                "label": "Rizz",
                "custom_id": "Rizz",
                "file_name": "",
            },
            {
                "label": "Bass",
                "custom_id": "Bass",
                "file_name": "",
            },
        ]
        for buttonConfig in buttons:
            sb_button = SB_Button()
            sb_button.setup(buttonConfig)
            self.add_item(sb_button)

class MusicBot(commands.Cog):
    vc : wavelink.Player = None
    current_track = None
    music_channel = None
    history = None

    def __init__(self, bot):
        self.bot = bot
        self.history = list()

    async def setup(self):
        """
        Sets up a connection to lavalink
        """
        await wavelink.NodePool.create_node(
            bot=self.bot, 
            host="localhost",
            port=2333, 
            password="Password"
        )

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        logger.info(f"{node} ready")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        await self.music_channel.send(f"Now playing: {track.title}")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        await self.music_channel.send(f"Finished: {track.title}")
        self.history.append(track.title)

    @commands.command(brief="Opens a soundboard with buttons")
    async def sb(self, ctx):
        view = SoundboardView(timeout=None)
        view.setup_buttons()
        view.player = self.vc
        await ctx.send("Your soundboard", view=view)

    @commands.command(brief="Joins bot into VC user is currently present in")
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        self.music_channel = ctx.message.channel
        if not channel: 
            await ctx.send("You need to be in a voice channel to use this command")
            return
        self.vc = await channel.connect(cls=wavelink.Player)
        await ctx.send(f"Connected to {channel.name}")

    @commands.command(brief="Leaves bot from VC")
    async def leave(self, ctx):
        channel = ctx.message.author.voice.channel
        if not channel: 
            await ctx.send("You need to be in a voice channel to use this command")
            return
        self.vc = await channel.disconnect(cls=wavelink.Player)
        await ctx.send(f"Connected to {channel.name}")
        

    @commands.command(brief="Search for a track from YT, SoundCloud, or Spotify")
    async def add(self, ctx, *title : str):
        #!search yt
        chosen_track = await wavelink.YouTubeTrack.search(query=" ".join(title), return_first=True)
        if chosen_track:
            self.current_track = chosen_track
            await ctx.send(f"Added {chosen_track.title} to the queue")
            self.vc.queue.put(chosen_track)

    @commands.command(brief="Plays the current track in queue")
    async def play(self, ctx):
        if self.current_track and self.vc:
            await self.vc.play(self.current_track)
            await ctx.send(f"Playing {self.current_track.title}")
    
    @commands.command(brief="Skips current song")
    async def skip(self, ctx):
        if self.vc.queue.is_empty:
            await ctx.send("Queue is empty")
            return
        self.current_track = self.vc.queue.get()
        await self.vc.play(self.current_track)

    @commands.command(brief="Pauses the current song")
    async def pause(self, ctx):
        await self.vc.pause(self.current_track)   
        await ctx.send(f"Paused {self.current_track.title}")

    @commands.command(brief="Resumes the current song")
    async def resume(self, ctx):
        await self.vc.resume(self.current_track)
        await ctx.send(f"Resumed {self.current_track.title}")

    @commands.command(brief="Stops the current song")
    async def stop(self, ctx):
        await self.vc.stop(self.current_track)
        await ctx.send(f"Stopped {self.current_track.title}")

async def setup(bot):
    music_bot = MusicBot(bot)
    await bot.add_cog(music_bot)
    await music_bot.setup()

    