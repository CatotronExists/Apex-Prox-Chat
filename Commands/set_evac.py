import nextcord
from nextcord.ext import commands
from Main import formatOutput, errorResponse, updatePresence, getVCs, updateJsonFile
from BotData.colors import *
from BotData.mapdata import MapData

class Command_set_evac_Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="set_evac", description="Set an evacuation voice channel that is used when switching maps", default_member_permissions=(nextcord.Permissions(administrator=True)))
    async def set_evac(self, interaction: nextcord.Interaction, vc_id = nextcord.SlashOption(name="vc", description="Enter VC ID", required=True)):
        global command
        command = {"name": interaction.application_command.name, "userID": interaction.user.id, "guildID": interaction.guild.id}
        formatOutput(output=f"/{command['name']} Used by {command['userID']} | @{interaction.user.name}", status="Normal", context=command["guildID"])

        try: await interaction.response.defer(ephemeral=True)
        except: pass # Discord can sometimes error on defer()

        try:
            channel = interaction.guild.get_channel(int(vc_id))
            if channel == None:
                embed = nextcord.Embed(title="**Error**", description="Invalid VC ID", color=Red)
                await interaction.edit_original_message(embed=embed)
                return

            elif channel.type != nextcord.ChannelType.voice:
                embed = nextcord.Embed(title="**Error**", description="Invalid VC ID", color=Red)
                await interaction.edit_original_message(embed=embed)
                return

            else: # Is a valid VC ID
                updateJsonFile("evacVC", channel.id)
                embed = nextcord.Embed(title="**Evacuation VC Set**", description=f"Evacuation VC set to {channel.name}", color=Green)
                await interaction.edit_original_message(embed=embed)

        except Exception as e: await errorResponse(e, command, interaction)

def setup(bot):
    bot.add_cog(Command_set_evac_Cog(bot))