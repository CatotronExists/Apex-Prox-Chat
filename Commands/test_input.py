import nextcord
from nextcord.ext import commands
from Main import formatOutput, errorResponse, regionCheck
from BotData.colors import *

class Command_test_input_Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="test_input", description="test coordinates")
    async def test_input(self, interaction: nextcord.Interaction, coords = nextcord.SlashOption(name="coords", description="enter coords, as (x,y)", required=True)):
        global command
        command = {"name": interaction.application_command.name, "userID": interaction.user.id, "guildID": interaction.guild.id}
        formatOutput(output=f"/{command['name']} Used by {command['userID']} | @{interaction.user.name}", status="Normal", context=command["guildID"])

        try: await interaction.response.defer(ephemeral=True)
        except: pass # Discord can sometimes error on defer()

        try:
            embed = nextcord.Embed(title="**testing coords**", description=f"fetching region...", color=White)
            await interaction.edit_original_message(embed=embed)

            player_pos = {'x': int(coords.split(",")[0]), 'y': int(coords.split(",")[1])}

            result = regionCheck(player_pos)
            print(result)

            embed = nextcord.Embed(title="**testing coords**", description=f"Player located in: **{result}**", color=Green)
            await interaction.edit_original_message(embed=embed)

        except Exception as e: await errorResponse(e, command, interaction)

def setup(bot):
    bot.add_cog(Command_test_input_Cog(bot))