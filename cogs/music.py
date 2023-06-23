import discord
from discord.ext import commands 
import settings 
import wavelink
import glob

#reloading the py file will cause the bot to break and have to restart if still connected to vc

logger = settings.logging.getLogger(__name__)

class SB_Button(discord.ui.Button):
    file_name : str = None 
    
    def setup(self, data):
        self.label = data['label']
        self.custom_id = data['custom_id']
        self.file_name = data['file_name']
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        soundboard_item = await wavelink.YouTubeTrack.search(query=self.file_name, return_first=True)
        if soundboard_item:
            await self.view.player.play(soundboard_item)
        
    
class SoundboardView(discord.ui.View):
    player : wavelink.Player = None 
    
    
    @discord.ui.button(label="Stop", 
                       style=discord.ButtonStyle.red)
    async def stop_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.player.stop()
    
    def setup_buttons(self):
        # Only up to 25 buttons in total
        # with the stop button above, only 24 are possible
        buttons = [ 
               {
                "label": "Applause",
                "custom_id": "applause",
                "file_name": "https://www.youtube.com/watch?v=jDOrc8FmDy4",
            },
            {
                "label": "Rizz",
                "custom_id": "rizz",
                "file_name": "https://www.youtube.com/watch?v=mq9VoNZdJqg",
            },
            {
                "label": "Yamete Kudasai",
                "custom_id": "yamete_kudasai",
                "file_name": "https://www.youtube.com/watch?v=gb4ZnGIhPD0",
            },
            {
                "label": "Deez Nuts",
                "custom_id": "deez_nuts",
                "file_name": "https://www.youtube.com/watch?v=66I78hXXwvk",
            },
            {
                "label": "Thomas Tank Engine",
                "custom_id": "thomas_tank",
                "file_name": "https://www.youtube.com/watch?v=gvTcmoJDVjg",
            },
            {
                "label": "Oof",
                "custom_id": "oof",
                "file_name": "https://www.youtube.com/watch?v=3w-2gUSus34",
            },
            {
                "label": "Do it",
                "custom_id": "do_it",
                "file_name": "https://www.youtube.com/watch?v=z2Qe1d4urfw",
            }
        ]
        
        for button_config in buttons:
            sb_button = SB_Button()
            sb_button.setup(button_config)
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
            password="changeme"
        )
    
    #events
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        logger.info(f"{node} is ready")
    
    # @commands.Cog.listener()
    # async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
    #     await self.music_channel.send(f"{track.title} started playing")
        
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)

    #commands
    
    @commands.command(brief="Manually joins the bot into the voice channel")
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        self.music_channel = ctx.message.channel
        if not channel:
            await ctx.send(f"You need to join a voice channel first.")
            return 
        self.vc = await channel.connect(cls=wavelink.Player)
        await ctx.send(f"Joined {channel.name}")

    @commands.command() 
    async def play(self, ctx, *, search: wavelink.YouTubeTrack):
        if not self.vc:
            self.vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        if self.vc.is_playing():
            self.vc.queue.put(search)
        else:
            await self.vc.play(search)

    @commands.command(brief="add song to queue")
    async def add(self, ctx, *title : str):
        chosen_track = await wavelink.YouTubeTrack.search(query=" ".join(title), return_first=True)
        if chosen_track:
            self.current_track = chosen_track
            await ctx.send(f"added {chosen_track.title} to queue")
            self.vc.queue.put(chosen_track)
            
    @commands.command(brief="Skips the current song")
    async def skip(self, ctx):
        if self.vc.queue.is_empty:
            await ctx.send("There are no more tracks!")
            return 
        self.current_track = self.vc.queue.get()
        await self.vc.play(self.current_track)
    
    @commands.command(brief="Pause playing song")
    async def pause(self, ctx):
        await self.vc.pause()
        await ctx.send(f"Paused current Track")            
        
    @commands.command(brief="Resumes current paused song")
    async def resume(self, ctx):
        await self.vc.resume()
        await ctx.send(f"Resuming current Track")
        
    @commands.command(brief="Stops current song")
    async def stop(self, ctx):
        await self.vc.stop()
        
    
    @commands.command(brief="Fast Forward n seconds")
    async def ff(self, ctx, seconds : int = 15):
        new_position = self.vc.position + seconds
        await self.vc.seek(new_position * 1000)
        
    @commands.command(brief="Go back n seconds")
    async def gb(self, ctx, seconds : int = 15):
        new_position = self.vc.position - seconds
        await self.vc.seek(new_position * 1000)
    
    @commands.command(brief="Shows song history")
    async def history(self, ctx):
        self.history.reverse()
        embed = discord.Embed(title="Song History")
        for song in self.history:
            track_info = song.split(" - ")
            embed.add_field(name=track_info[1], value=track_info[0], inline=False)

        await ctx.send(embed=embed)

    @commands.command(brief="Leaves current voice channel")
    async def leave(self, ctx):
        if self.vc:
            await self.vc.disconnect()
            await ctx.send(f"Left {self.vc.channel.name}")
        else:
            await ctx.send("Not in a voice channel")
            
    
    @commands.command(brief="Opens a soundboard with buttons")
    async def sb(self, ctx):
        view = SoundboardView(timeout=None)
        view.setup_buttons()
        view.player = self.vc
        await ctx.send("Your soundboard", view=view)
        
async def setup(bot):
    music_bot = MusicBot(bot)
    await bot.add_cog(music_bot)
    await music_bot.setup()

