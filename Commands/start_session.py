import nextcord
from nextcord.ext import commands
from Main import formatOutput, errorResponse, updatePresence, getVCs, updateJsonFile
from BotData.colors import *
from BotData.mapdata import MapData

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
            if getVCs() != None: # Channels already exist, so infer a session is already running
                embed = nextcord.Embed(title="**Error**", description="There is already an active session. Please end the current session before starting a new one", color=Red)
                await interaction.edit_original_message(embed=embed)
                return

            # Session not running, start one
            embed = nextcord.Embed(title="**Starting Up Proximity Chat Session (Stage 1/3)**", description=f"Prepairing...\n\n**Map:** {map}", color=White)
            await interaction.edit_original_message(embed=embed)

            map_data = MapData[map]

            embed = nextcord.Embed(title="**Starting Up Proximity Chat Session (Stage 2/3)**", description=f"Creating Voice Channel Catergory", color=White)
            await interaction.edit_original_message(embed=embed)

            catergory = await interaction.guild.create_category("Proximity Chat")
            updateJsonFile("vcCatergory", catergory.id)

            embed = nextcord.Embed(title="**Starting Up Proximity Chat Session (Stage 3/3)**", description=f"Creating Voice Channels...", color=White)
            await interaction.edit_original_message(embed=embed)

            vc_ids = {}
            lobby_vc = await interaction.guild.create_voice_channel("LOBBY", category=catergory)
            vc_ids["LOBBY"] = lobby_vc.id

            dead_vc = await interaction.guild.create_voice_channel("DEAD", category=catergory, overwrites={interaction.guild.default_role: nextcord.PermissionOverwrite(view_channel=False)})
            vc_ids["DEAD"] = dead_vc.id

            final_vc = await interaction.guild.create_voice_channel("FINAL RING", category=catergory, overwrites={interaction.guild.default_role: nextcord.PermissionOverwrite(view_channel=False)})
            vc_ids["FINAL RING"] = final_vc.id

            for poi in map_data.keys():
                vc = await interaction.guild.create_voice_channel(poi, category=catergory, overwrites={interaction.guild.default_role: nextcord.PermissionOverwrite(view_channel=False)})
                vc_ids[poi] = vc.id

            updateJsonFile("vcList", vc_ids)
            updateJsonFile("map", map)

            embed = nextcord.Embed(title="**Proximity Chat Session Started**", description=f"Voice Channels Created", color=Green)
            await interaction.edit_original_message(embed=embed)

            await updatePresence(f"Proximity Chat session on {map}!")

        except Exception as e: await errorResponse(e, command, interaction)

def setup(bot):
    bot.add_cog(Command_start_session_Cog(bot))