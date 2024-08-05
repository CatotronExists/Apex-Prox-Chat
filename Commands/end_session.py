import nextcord
from nextcord.ext import commands
from Main import formatOutput, errorResponse, updatePresence, getGameData
from BotData.colors import *
from Keyss import DB

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
            if getGameData() == None:
                embed = nextcord.Embed(title="**Error**", description="There is no active session to end", color=Red)
                await interaction.edit_original_message(embed=embed)
                formatOutput(output="   There is no active session to end", status="Error", context=command['guildID'])
                return

            embed = nextcord.Embed(title="**Ending Proximity Chat Session (Stage 1/3)**", description=f"Prepairing...", color=White)
            await interaction.edit_original_message(embed=embed)

            IDs = DB.Main.IDs.find_one({"vcCatergory": {"$exists": True}})
            embed = nextcord.Embed(title="**Ending Proximity Chat Session (Stage 2/3)**", description=f"Deleting Voice Channels...", color=White)
            await interaction.edit_original_message(embed=embed)

            for id in IDs["vcList"]:
                vc = interaction.guild.get_channel(IDs["vcList"][id])
                await vc.delete()

            embed = nextcord.Embed(title="**Ending Proximity Chat Session (Stage 3/3)**", description=f"Cleaning Up...", color=White)
            await interaction.edit_original_message(embed=embed)

            catergory = interaction.guild.get_channel(IDs["vcCatergory"])
            await catergory.delete()

            DB.Main.IDs.delete_one({"vcCatergory": catergory.id}) # Wipe VC IDs
            DB.Main.GameData.delete_one({"map": {"$exists": True}}) # Wipe Game Data

            embed = nextcord.Embed(title="**Proximity Chat Session Ended**", description=f"Voice Channels Deleted", color=Green)
            await interaction.edit_original_message(embed=embed)

            await updatePresence("for /start_session")

        except Exception as e: await errorResponse(e, command, interaction)

def setup(bot):
    bot.add_cog(Command_end_session_Cog(bot))