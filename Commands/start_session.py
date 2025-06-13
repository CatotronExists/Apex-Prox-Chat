import nextcord
from nextcord.ext import commands
from Main import formatOutput, errorResponse, updatePresence, getVCs, updateJsonFile
from BotData.colors import *
from BotData.mapdata import MapData

class Command_start_session_Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="start_session", description="Start a poximity chat session (Creates Voice Channels)", default_member_permissions=(nextcord.Permissions(administrator=True)))
    async def start_session(self, interaction: nextcord.Interaction,
        map = nextcord.SlashOption(name="map", description="Select Map", required=True, choices={"E-District (BR)": "E-District", "World's Edge (BR)": "Worlds Edge", "Broken Moon (BR)": "Broken Moon", "Monument (Mixtape)": "Monument", "Fragment East (Mixtape)": "Fragment East", "Lava Siphon (Mixtape)": "Lava Siphon"}),
        game_mode = nextcord.SlashOption(name="game_mode", description="Select Game Mode (Required when picking a (Mixtape) map)", required=False, choices={"BR": "BR", "Control": "Control", "TDM": "TDM", "Gun Run": "Gun Run", "Arenas": "Arenas"})):

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

            br_maps = ["Kings Canyon", "Worlds Edge", "Storm Point", "Olympus", "Broken Moon", "E-District"]
            mixtape_maps = ["Thunderdome"]
            arenas_maps = ["Overflow", "Drop-off", "Encore"]

            if map in br_maps: # If BR map
                game_mode = "BR" # Set game mode to BR

            elif map in mixtape_maps: # If Mixtape map
                if game_mode == None:
                    embed = nextcord.Embed(title="**Error**", description="You must select a game mode when picking a Mixtape map", color=Red)
                    await interaction.edit_original_message(embed=embed)
                    return

                elif game_mode not in ["Control", "TDM", "Gun Run"]: # If game mode is not a valid Mixtape game mode
                    embed = nextcord.Embed(title="**Error**", description="You must select a valid Mixtape game mode", color=Red)
                    await interaction.edit_original_message(embed=embed)
                    return

            elif map in arenas_maps: # If Arenas map
                game_mode = "Arenas" # Set game mode to Arenas

            # Session not running, start one
            embed = nextcord.Embed(title="**Starting Up Proximity Chat Session (Stage 1/2)**", description=f"Prepairing...\n\n**Map:** {map}", color=White)
            await interaction.edit_original_message(embed=embed)

            map_data = MapData[map]
            pois = []
            for poi in map_data.keys():
                pois.append(poi)

            pois.insert(0, "FINAL RING")
            pois.insert(0, "DEAD")
            pois.insert(0, "LOBBY")

            vcs_to_create = len(pois) # number of vcs to create

            embed = nextcord.Embed(title="**Starting Up Proximity Chat Session (Stage 2/2)**", description=f"Creating Voice Channels\n\n**Map:** {map}", color=White)
            await interaction.edit_original_message(embed=embed)

            vc_catergories = []
            vc_ids = {}
            for i in range(0, vcs_to_create, 50):
                catergory = await interaction.guild.create_category(f"Proximity Chat {i//50 + 1}")
                vc_catergories.append(catergory.id)
                vcs = pois[i:i+50]

                for poi in vcs:
                    if poi == "LOBBY": # Make lobby open
                        vc = await interaction.guild.create_voice_channel(
                            name=poi,
                            category=catergory
                        )

                    else:
                        vc = await interaction.guild.create_voice_channel(
                            name=poi,
                            category=catergory,
                            overwrites={interaction.guild.default_role: nextcord.PermissionOverwrite(view_channel=False)}
                        )
                    vc_ids[poi] = vc.id

            updateJsonFile("vcList", vc_ids)
            updateJsonFile("vcCatergories", vc_catergories)
            updateJsonFile("map", map)

            embed = nextcord.Embed(title="**Proximity Chat Session Started**", description=f"Voice Channels Created", color=Green)
            embed.set_footer(text=f"Map: {map}")
            await interaction.edit_original_message(embed=embed)

            await updatePresence(f"Proximity Chat session on {map}!")

        except Exception as e: await errorResponse(e, command, interaction)

def setup(bot):
    bot.add_cog(Command_start_session_Cog(bot))