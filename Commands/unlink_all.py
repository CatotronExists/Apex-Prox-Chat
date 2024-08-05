import nextcord
from nextcord.ext import commands
from Main import formatOutput, errorResponse
from BotData.colors import *
from Keyss import DB

class Command_unlink_all_Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="unlink_all", description="Unlink all discord to in-game accounts, THIS CANNOT BE UNDONE", default_member_permissions=(nextcord.Permissions(administrator=True)))
    async def unlink_all(self, interaction: nextcord.Interaction):
        global command
        command = {"name": interaction.application_command.name, "userID": interaction.user.id, "guildID": interaction.guild.id}
        formatOutput(output=f"/{command['name']} Used by {command['userID']} | @{interaction.user.name}", status="Normal", context=command["guildID"])

        try: await interaction.response.defer(ephemeral=True)
        except: pass # Discord can sometimes error on defer()

        try:
            embed = nextcord.Embed(title="**UNLINKING ALL ACCOUNTS (Stage 1/)**", description=f"Gathering links...", color=White)
            await interaction.edit_original_message(embed=embed)

            links = list(DB.Main.PlayerData.find()) # Get all linked accounts

            embed = nextcord.Embed(title="**UNLINKING ALL ACCOUNTS (Stage 2/2)**", description=f"Unlinking...", color=White)
            await interaction.edit_original_message(embed=embed)

            for link in links: # Unlink all accounts
                DB.Main.PlayerData.delete_one({"discordID": link["discordID"]})

            embed = nextcord.Embed(title="**ALL ACCOUNTS UNLINKED**", description=f"Unlinking Complete", color=Green)
            await interaction.edit_original_message(embed=embed)

        except Exception as e: await errorResponse(e, command, interaction)

def setup(bot):
    bot.add_cog(Command_unlink_all_Cog(bot))