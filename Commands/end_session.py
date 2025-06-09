import nextcord
from nextcord.ext import commands
from Main import formatOutput, errorResponse, updatePresence, getVCs, updateJsonFile, readJsonFile
from BotData.colors import *

class Command_end_session_Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="end_session", description="End poximity chat session (Removes Voice Channels)", default_member_permissions=(nextcord.Permissions(administrator=True)))
    async def end_session(self, interaction: nextcord.Interaction):
        global command
        command = {"name": interaction.application_command.name, "userID": interaction.user.id, "guildID": interaction.guild.id}
        formatOutput(output=f"/{command['name']} Used by {command['userID']} | @{interaction.user.name}", status="Normal", context=command["guildID"])

        try: await interaction.response.defer(ephemeral=True)
        except: pass # Discord can sometimes error on defer()

        try:
            IDs = getVCs()
            if IDs == None: # No Channels exist, so infer no session is running
                embed = nextcord.Embed(title="**Error**", description="There is no active session to end", color=Red)
                await interaction.edit_original_message(embed=embed)
                return

            # Session is running, end it
            embed = nextcord.Embed(title="**Ending Proximity Chat Session (Stage 1/2)**", description=f"Deleting Voice Channels...", color=White)
            await interaction.edit_original_message(embed=embed)

            for name, id in IDs.items():
                vc = interaction.guild.get_channel(id)
                if vc != None: await vc.delete()

            updateJsonFile("vcList", None)

            embed = nextcord.Embed(title="**Ending Proximity Chat Session (Stage 2/2)**", description=f"Cleaning Up Categories", color=White)
            await interaction.edit_original_message(embed=embed)

            vc_catergory_id = readJsonFile("vcCatergories")

            for catergory_id in vc_catergory_id:
                catergory = interaction.guild.get_channel(catergory_id)
                if catergory != None: await catergory.delete()

            updateJsonFile("map", None)
            updateJsonFile("gamemode", None)
            updateJsonFile("gameState", None)
            updateJsonFile("movementLocked", False)
            updateJsonFile("vcCatergories", [])

            embed = nextcord.Embed(title="**Proximity Chat Session Ended**", description=f"Voice Channels Deleted", color=Green)
            await interaction.edit_original_message(embed=embed)

            await updatePresence("for /start_session")

        except Exception as e: await errorResponse(e, command, interaction)

def setup(bot):
    bot.add_cog(Command_end_session_Cog(bot))