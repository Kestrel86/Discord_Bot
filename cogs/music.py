import discord
from discord.ext import commands 
import settings 
import wavelink

logger = settings.logging.getLogger(__name__)

class SBbutton(discord.ui.Button):
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
                "file_name": ""
            }
        ]