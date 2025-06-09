import nextcord
from nextcord.ext import commands
from Main import formatOutput, errorResponse, addPlayer, getPlayer, updatePlayer, removePlayer
from BotData.colors import *

class MainView(nextcord.ui.View):
    def __init__(self, interaction: nextcord.Interaction):
        super().__init__(timeout=60)
        player = getPlayer(interaction.user.id) # Get player data
        self.player = player
        self.interaction = interaction

        link_button = nextcord.ui.Button(style=nextcord.ButtonStyle.green, label="Link")
        link_button.callback = self.create_callback("link")
        self.add_item(link_button)

        if player['role'] == "Player":
            toggle_button = nextcord.ui.Button(style=nextcord.ButtonStyle.gray, label="Player (Change)")
        else:
            toggle_button = nextcord.ui.Button(style=nextcord.ButtonStyle.gray, label="Observer (Change)")

        toggle_button.callback = self.create_callback("toggle")
        self.add_item(toggle_button)

        unlink_button = nextcord.ui.Button(style=nextcord.ButtonStyle.red, label="Unlink")
        unlink_button.callback = self.create_callback("unlink")
        self.add_item(unlink_button)

    def create_callback(self, action):
        async def callback(interaction: nextcord.Interaction):
            if action == "link":
                await interaction.response.send_modal(LinkModal(self.interaction))
            elif action == "toggle":
                if self.player['role'] == "Player":
                    self.player['role'] = "Observer" # Switch to observer
                else:
                    self.player['role'] = "Player" # Switch to player

                updatePlayer(self.interaction.user.id, 'role', self.player['role'])

                if self.player['inGameName'] == None: # Send embed
                    embed = nextcord.Embed(title=f"**/Link {self.interaction.user.name.capitalize()}**", description=f"**No-In-Game Name Linked**\nLink yourself using the button below!", color=White)
                else:
                    embed = nextcord.Embed(title=f"**/Link {self.interaction.user.name.capitalize()}**", description=f"**In-Game Name Linked**\n{self.player['inGameName']}\n\nChanged username? or made a typo?...Link again!", color=White)

                await interaction.response.edit_message(embed=embed, view=MainView(self.interaction))

            elif action == "unlink":
                removePlayer(self.interaction.user.id)
                embed = nextcord.Embed(title=f"**/Link {self.interaction.user.name.capitalize()}**", description=f"**Unlinked**", color=Red)
                await interaction.response.edit_message(embed=embed, view=None)

        return callback

class LinkModal(nextcord.ui.Modal):
    def __init__(self, interaction: nextcord.Interaction):
        super().__init__(title="Link your IGN", timeout=60)
        player = getPlayer(interaction.user.id)
        self.player = player
        self.interaction = interaction

        self.input = nextcord.ui.TextInput(
            label="In-Game Name",
            placeholder="Enter your In-Game Name",
            required=True,
            min_length=1,
            max_length=30,
        )

        self.add_item(self.input)
        self.input.callback = self.callback

    async def callback(self, interaction: nextcord.Interaction):
        try:
            updatePlayer(self.interaction.user.id, 'inGameName', self.input.value)

            embed = nextcord.Embed(title=f"**/Link {self.interaction.user.name.capitalize()}**", description=f"**In-Game Name Linked**\n{self.input.value}\n\nChanged username? or made a typo?...Link again!", color=White)
            await interaction.response.edit_message(embed=embed, view=MainView(self.interaction))

        except Exception as e: await errorResponse(e, command, interaction)

class Command_link_Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="link", description="Opens a menu to link your IGN to your Discord Account, Required so the bot can recognize you")
    async def link(self, interaction: nextcord.Interaction):
        global command
        command = {"name": interaction.application_command.name, "userID": interaction.user.id, "guildID": interaction.guild.id}
        formatOutput(output=f"/{command['name']} Used by {command['userID']} | @{interaction.user.name}", status="Normal", context=command["guildID"])

        try: await interaction.response.defer(ephemeral=True)
        except: pass # Discord can sometimes error on defer()

        try:
            player = getPlayer(interaction.user.id)
            if player == None: # Discord user has not been linked
                player = {"inGameName": None, "currentRegion": None, "discordID": interaction.user.id, "role": "Player", "currentlyObserving": None, "isAlive": True, "lastActionTime": None}
                addPlayer(player)
                embed = nextcord.Embed(title=f"**/Link {interaction.user.name.capitalize()}**", description=f"**No In-Game Name Linked**\nLink yourself using the button below!", color=White)
                await interaction.edit_original_message(embed=embed, view=MainView(interaction))

            else: # Discord user has linked before
                embed = nextcord.Embed(title=f"**/Link {interaction.user.name.capitalize()}**", description=f"**In-Game Name Linked**\n{player['inGameName']}\n\nChanged username? or made a typo?...Link again!", color=White)
                await interaction.edit_original_message(embed=embed, view=MainView(interaction))

        except Exception as e: await errorResponse(e, command, interaction)

def setup(bot):
    bot.add_cog(Command_link_Cog(bot))