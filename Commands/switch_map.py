import nextcord
from nextcord.ext import commands
from Main import formatOutput, errorResponse, updatePresence, getVCs, updateJsonFile, readJsonFile, getAllPlayers
from BotData.mapdata import MapData
from BotData.colors import *

class Command_switch_map_Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="switch_map", description="Switch map for proximity chat (It is recommended to first have set an evac vc)", default_member_permissions=(nextcord.Permissions(administrator=True)))
    async def switch_map(self, interaction: nextcord.Interaction,
        map = nextcord.SlashOption(name="map", description="Select Map", required=True, choices={"World's Edge (BR)": "Worlds Edge", "Olympus (BR)": "Olympus", "Broken Moon (BR)": "Broken Moon", "E-District (BR)": "E-District"})):

        global command
        command = {"name": interaction.application_command.name, "userID": interaction.user.id, "guildID": interaction.guild.id}
        formatOutput(output=f"/{command['name']} Used by {command['userID']} | @{interaction.user.name}", status="Normal", context=command["guildID"])

        try: await interaction.response.defer(ephemeral=True)
        except: pass # Discord can sometimes error on defer()

        try:
            IDs = getVCs()
            if IDs == None: # No Channels exist, so infer no session is running
                embed = nextcord.Embed(title="**Error**", description="There is no active session to switch map for, use /start_session", color=Red)
                await interaction.edit_original_message(embed=embed)
                return

            # Evac everyone, if set
            evacVC = readJsonFile("evacVC")
            if evacVC != None:

                embed = nextcord.Embed(title="**Changing Proximity Chat Map (Stage 1/6)**", description=f"Evacuating everyone to Evac VC...", color=White)
                await interaction.edit_original_message(embed=embed)

                evac = interaction.guild.get_channel(evacVC)
                if evac != None:
                    for player in getAllPlayers():
                        try:
                            user = interaction.guild.get_member(player['discordID'])
                            await user.move_to(evac)
                        except: pass

            # Delete VCs and catergories
            embed = nextcord.Embed(title="**Changing Proximity Chat Map (Stage 2/6)**", description=f"Deleting Voice Channels...", color=White)
            await interaction.edit_original_message(embed=embed)

            for name, id in IDs.items():
                vc = interaction.guild.get_channel(id)
                if vc != None: await vc.delete()

            updateJsonFile("vcList", None)

            embed = nextcord.Embed(title="**Changing Proximity Chat Map (Stage 3/6)**", description=f"Deleting Categories...", color=White)
            await interaction.edit_original_message(embed=embed)

            vc_catergory_id = readJsonFile("vcCatergories")

            for catergory_id in vc_catergory_id:
                catergory = interaction.guild.get_channel(catergory_id)
                if catergory != None: await catergory.delete()

            updateJsonFile("map", None)
            updateJsonFile("vcCatergories", [])

            # Create new catergory and VCs

            embed = nextcord.Embed(title="**Changing Proximity Chat Map (Stage 4/6)**", description=f"Prepairing...\n\n**Map:** {map}", color=White)
            await interaction.edit_original_message(embed=embed)

            map_data = MapData[map]
            pois = []
            for poi in map_data.keys():
                pois.append(poi)

            pois.insert(0, "FINAL RING")
            pois.insert(0, "DEAD")
            pois.insert(0, "LOBBY")

            vcs_to_create = len(pois) # number of vcs to create

            embed = nextcord.Embed(title="**Changing Proximity Chat Map (Stage 5/6) **", description=f"Creating Voice Channels\n\n**Map:** {map}", color=White)
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

            embed = nextcord.Embed(title="**Changing Proximity Chat Map (Stage 6/6)**", description=f"Returning players to Lobby", color=White)
            await interaction.edit_original_message(embed=embed)

            lobby = interaction.guild.get_channel(vc_ids["LOBBY"])
            for player in getAllPlayers():
                try:
                    user = interaction.guild.get_member(player['discordID'])
                    await user.move_to(lobby)
                except: pass

            updateJsonFile("vcList", vc_ids)
            updateJsonFile("vcCatergories", vc_catergories)
            updateJsonFile("map", map)

            embed = nextcord.Embed(title="**Proximity Chat Map Changed**", description=f"Switched to {map}", color=Green)
            embed.set_footer(text=f"Map: {map}")
            await interaction.edit_original_message(embed=embed)

            await updatePresence(f"Proximity Chat session on {map}!")

        except Exception as e: await errorResponse(e, command, interaction)

def setup(bot):
    bot.add_cog(Command_switch_map_Cog(bot))