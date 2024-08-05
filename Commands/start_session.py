import nextcord
from nextcord.ext import commands
from Main import formatOutput, errorResponse, updatePresence, getGameData
from BotData.colors import *
from BotData.mapdata import MapData
from Keys import DB

class Command_start_session_Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="start_session", description="Start a poximity chat session (Creates Voice Channels)", default_member_permissions=(nextcord.Permissions(administrator=True)))
    async def start_session(self, interaction: nextcord.Interaction, map = nextcord.SlashOption(name="map", description="Select Map", required=True, choices={map:map for map in MapData.keys()})):
        global command
        command = {"name": interaction.application_command.name, "userID": interaction.user.id, "guildID": interaction.guild.id}
        formatOutput(output=f"/{command['name']} Used by {command['userID']} | @{interaction.user.name}", status="Normal", context=command["guildID"])

        try: await interaction.response.defer(ephemeral=True)
        except: pass # Discord can sometimes error on defer()

        try:
            if getGameData() != None:
                embed = nextcord.Embed(title="**Error**", description="There is already an active session. Please end the current session before starting a new one", color=Red)
                await interaction.edit_original_message(embed=embed)
                formatOutput(output="   There is already an active session. Please end the current session before starting a new one", status="Error", context=command['guildID'])
                return

            embed = nextcord.Embed(title="**Starting Up Proximity Chat Session (Stage 1/2)**", description=f"Prepairing...\n\n**Map:** {map}", color=White)
            await interaction.edit_original_message(embed=embed)

            DB.Main.GameData.insert_one({"map": map, "status": "Lobby"})

            map_data = MapData[map]

            embed = nextcord.Embed(title="**Starting Up Proximity Chat Session (Stage 2/2)**", description=f"Creating Voice Channels...", color=White)
            await interaction.edit_original_message(embed=embed)

            catergory = await interaction.guild.create_category("Proximity Chat")
            id_data = {"vcCatergory": catergory.id, "vcList": {}}

            lobby_vc = await interaction.guild.create_voice_channel("LOBBY", category=catergory)
            id_data["vcList"]["LOBBY"] = lobby_vc.id

            dead_vc = await interaction.guild.create_voice_channel("DEAD", category=catergory, overwrites={interaction.guild.default_role: nextcord.PermissionOverwrite(view_channel=False)})
            id_data["vcList"]["DEAD"] = dead_vc.id

            for poi, poi_data in map_data.items():
                vc = await interaction.guild.create_voice_channel(poi, category=catergory, overwrites={interaction.guild.default_role: nextcord.PermissionOverwrite(view_channel=False)})
                id_data["vcList"][poi] = vc.id

            DB.Main.IDs.insert_one(id_data)

            embed = nextcord.Embed(title="**Proximity Chat Session Started**", description=f"Voice Channels Created", color=Green)
            await interaction.edit_original_message(embed=embed)

            await updatePresence(f"Session on {map}")

        except Exception as e: await errorResponse(e, command, interaction)

def setup(bot):
    bot.add_cog(Command_start_session_Cog(bot))