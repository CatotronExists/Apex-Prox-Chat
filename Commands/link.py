import nextcord
from nextcord.ext import commands
from Main import formatOutput, errorResponse, addPlayer, getPlayer, updatePlayer
from BotData.colors import *

class Command_link_Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="link", description="Link your IGN to your Discord Account, Required so the bot can recognize you")
    async def link(self, interaction: nextcord.Interaction, ign = nextcord.SlashOption(name="ign", description="Type in your EXACT In-Game Name", required=True)):
        global command
        command = {"name": interaction.application_command.name, "userID": interaction.user.id, "guildID": interaction.guild.id}
        formatOutput(output=f"/{command['name']} Used by {command['userID']} | @{interaction.user.name}", status="Normal", context=command["guildID"])

        try: await interaction.response.defer(ephemeral=True)
        except: pass # Discord can sometimes error on defer()

        try:
            embed = nextcord.Embed(title="**Linking IGN**", description=f"Linking IGN: `{ign}` to Discord Account: `{interaction.user.name}`\nPlease Wait, this will take a few moments", color=White)
            await interaction.edit_original_message(embed=embed)

            if getPlayer(interaction.user.id) == None: # Discord user has not linked before
                player_data = {"inGameName": ign, "currentRegion": None, "isAlive": None, "discordID": interaction.user.id}
                addPlayer(player_data) # Add player to JSON file

            else: # Discord user has linked before, so update their IGN
                updatePlayer(interaction.user.id, "inGameName", ign)

            embed = nextcord.Embed(title="**Linking IGN**", description=f"Linking Complete\n{interaction.user.name} ({interaction.user.id}) 🔗 {ign}", color=Green)
            embed.set_footer(text="Mistyped your IGN? run /link again to update it!")
            await interaction.edit_original_message(embed=embed)

        except Exception as e: await errorResponse(e, command, interaction)

def setup(bot):
    bot.add_cog(Command_link_Cog(bot))