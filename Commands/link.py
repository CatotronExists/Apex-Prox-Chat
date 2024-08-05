import nextcord
from nextcord.ext import commands
from Main import formatOutput, errorResponse
from BotData.colors import *
from Keys import DB

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

            if DB.Main.PlayerData.find_one({"discordID": interaction.user.id}) == None: # If user has not linked before
                DB.Main.PlayerData.insert_one({
                    "discordID": interaction.user.id,
                    "IGN": ign,
                    "currentPOI": None,
                    "healthState": "Alive"
                })

            else: # If user has linked before -> update
                DB.Main.PlayerData.update_one({"discordID": interaction.user.id}, {"$set": {"IGN": ign}})

            embed = nextcord.Embed(title="**Linking IGN**", description=f"Linking Complete\n{interaction.user.name}/{interaction.user.id} 🔗 {ign}", color=Green)
            await interaction.edit_original_message(embed=embed)

        except Exception as e: await errorResponse(e, command, interaction)

def setup(bot):
    bot.add_cog(Command_link_Cog(bot))