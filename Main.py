import datetime
import time
import asyncio
import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from BotData.colors import *
from BotData.mapdata import MapData
from Keys import *
import LiveApex
import json
from filelock import FileLock
import os
import traceback
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Command List
command_list = ["start_session", "end_session", "link", "unlink_all", "set_evac", "switch_map"]

# player Events
player_events_list = ["inventoryPickUp", "weaponSwitched", "inventoryUse", "ammoUsed", "grenadeThrown", "inventoryDrop", "blackMarketAction", "playerUltimateCharged", "playerAbilityUsed", "playerUpgradeTierChanged", "legendUpgradeSelected", "playerStatChanged", "bannerCollected", "wraithPortal", "ziplineUsed", "warpGateUsed", "arenasItemSelected", "arenasItemDeselected"]
attacker_victim_list = ["playerDamaged", "playerDowned", "playerKilled", "revenantForgedShadowDamaged", "gibraltarShieldAbsorbed"]

# Discord Setup
intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)

event_queue = asyncio.Queue(maxsize=1000)

### Format Terminal
def formatOutput(output, status, context):
    current_time = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')[:-7]
    if status == "Normal": print(f"{current_time} || {CBOLD} {context} {CLEAR} {output}")
    elif status == "Good": print(f"{CGREEN}{current_time} || {CBOLD} {context} {CLEAR} {output} {CLEAR}")
    elif status == "Error": print(f"{CRED}{current_time} || {CBOLD} {context} {CLEAR} {output} {CLEAR}")
    elif status == "Warning": print(f"{CYELLOW}{current_time} || {CBOLD} {context} {CLEAR} {output} {CLEAR}")

### Error Handler
async def errorResponse(error, command, interaction: Interaction):
    embed = nextcord.Embed(title="**Error**", description=f"Something went wrong while running `/{command['name']}`\nDid you mistype an entry or not follow the format?\nError: {error}", color=Red)
    await interaction.response.edit_message(embed=embed, view=None)
    formatOutput(output=f"   Something went wrong while running /{command['name']}. Error: {error}", status="Error", guildID=command['guildID'])

def logEvent(event, status, traceback): # Log Event to terminal and text file
    current_time = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')[:-7]
    if status == "Error":
        with open("log.txt", "a") as f:
            f.write(f"{current_time} || {status} || {event}\n")
            f.write(f"---- ERROR LOG ---\n{traceback}\n")
            formatOutput(event, status="Error", context="Log")
    else: formatOutput(event, status=status, context="Log")

### Handy Functions
map_cache = None
async def load_map_cache():
    global map_cache
    try:
        with FileLock("data.json.lock"):
            with open("data.json", "r") as f:
                data = json.load(f)
        map_cache = data
        formatOutput("Map cache loaded", status="Good", context="Cache")

    except Exception as e: logEvent(f"Error updating cache: {e}", status="Error", traceback=traceback.format_exc())

async def flush_map_cache():
    global map_cache
    try:
        if map_cache is not None:
            with FileLock("data.json.lock"):
                with open("data.json.tmp", "w") as f:
                    json.dump(map_cache, f, indent=4)
                os.replace("data.json.tmp", "data.json")
                formatOutput("Map cache flushed", status="Good", context="Cache")

    except Exception as e: logEvent(f"Error flushing map cache: {e}", status="Error", traceback=traceback.format_exc())

player_cache = None
async def load_player_cache():
    global player_cache
    try:
        with FileLock("playerData.json.lock"):
            with open("playerData.json", "r") as f:
                data = json.load(f)
            player_cache = data
            formatOutput("Player cache loaded", status="Good", context="Cache")

    except Exception as e: logEvent(f"Error loading player cache: {e}", status="Error", traceback=traceback.format_exc())

async def flush_player_cache():
    global player_cache
    try:
        if player_cache is not None:
            with FileLock("playerData.json.lock"):
                with open("playerData.json.tmp", "w") as f:
                    json.dump(player_cache, f, indent=4)
                os.replace("playerData.json.tmp", "playerData.json")
                formatOutput("Player cache flushed", status="Good", context="Cache")

    except Exception as e: logEvent(f"Error flushing player cache: {e}", status="Error", traceback=traceback.format_exc())

def readJsonFile(key):
    return map_cache[key]

def updateJsonFile(key, value):
    global map_cache
    map_cache[key] = value

def getVCs():
    return map_cache['vcList']

def getAllPlayers():
    return player_cache['players']

def getPlayer(identifier):
    players = getAllPlayers()
    if isinstance(identifier, int): # By discordID
        for player in players:
            if player['discordID'] == identifier:
                return player
    else: # By inGameName
        for player in players:
            if player['inGameName'] == identifier:
                return player
    return None

def addPlayer(player_data):
    global player_cache
    players = getAllPlayers()
    players.append(player_data)

def removePlayer(identifier):
    global player_cache
    players = getAllPlayers()
    for player in players:
        if player['discordID'] == identifier or player['inGameName'] == identifier:
            players.remove(player)
            break

def updatePlayer(identifier, key, value):
    global player_cache
    for player in player_cache['players']:
        if player.get('discordID') == identifier or player.get('inGameName') == identifier:
            player[key] = value

def checkLastAction(identifier):
    player = getPlayer(identifier)
    if player is not None:
        return player.get('lastActionTime')
    return None

async def updatePresence(status):
    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=status))

##### Startup Terminal
start_time = datetime.datetime.now()
formatOutput(f"{CBOLD}STARTING UP{CLEAR}", status="Normal", context="STARTUP")

# Load Commands
formatOutput("Loading Commands...", status="Normal", context="STARTUP")
for command in command_list:
    try:
        bot.load_extension(f"Commands.{command}")
        formatOutput(f"    /{command} Successfully Loaded", status="Good", context="STARTUP")
    except Exception as e:
        formatOutput(f"    /{command} Failed to Load // Error: {e}", status="Warning", context="STARTUP")
formatOutput("Commands Loaded", status="Normal", context="STARTUP")
formatOutput("Connecting to Discord...", status="Normal", context="STARTUP")

@bot.event
async def on_ready():
    startup_time = round((datetime.datetime.now() - start_time).total_seconds() * 1000)
    formatOutput(f"{bot.user.name} has connected to Discord (Took {startup_time}ms)", status="Good", context="STARTUP")

    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="for /start_session"))
    formatOutput("---------------------------------", status="Normal", context="STARTUP")

##### Logic
def rayCastAlgorithm(point, polygon):
    x, y = point
    inside = False
    n = len(polygon)

    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]

        # Check if the ray intersects the edge of the polygon
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside

    return inside
def regionCheck(player_pos):
    player_x = player_pos['x']
    player_y = player_pos['y']
    point = (player_x, player_y)

    regions = MapData[readJsonFile("map")]

    for region_name, polygon in regions.items():
        if rayCastAlgorithm(point, polygon):
            return region_name

    return None

async def playerMover(player, pos, type, delay): # Move user to VC
    try:
        player_data = getPlayer(player)
        if player_data is None: return # If player data is not found, do not move user
        try:
            guild = bot.get_guild(GUILD_ID)
            user = guild.get_member(player_data['discordID'])
            if user is None: return # If user is not found, do not move user
        except: return
        if delay != 0: await asyncio.sleep(delay) # Delay moving user if specified

        if type == "normal": # Normal Movement
            if player_data['isAlive'] == False: return # if dead dont move
            if player_data['lastActionTime'] is not None and int(time.time()) - player_data['lastActionTime'] < 2: return # If last action was less than 2 seconds ago, do not move player
            if readJsonFile("movementLocked") == True: return # If movement is locked, do not move player

            player_region = player_data['currentRegion']
            closest_region = regionCheck(pos)
            if closest_region != None:
                if player_region != closest_region:
                    new_vc = getVCs()[closest_region]
                    new_vc = await bot.fetch_channel(new_vc)

                    try:
                        await nextcord.Member.move_to(user, new_vc)
                    except: pass
                    updatePlayer(player_data['discordID'], "currentRegion", closest_region)
                    logEvent(f"Moved {player} to {closest_region}", status="Normal", traceback=None)

        elif type == "lobby": # Lobby Movement
            new_vc = getVCs()['LOBBY']
            new_vc = await bot.fetch_channel(new_vc)

            try:
                await nextcord.Member.move_to(user, new_vc)
            except: pass
            updatePlayer(player_data['discordID'], "currentRegion", "LOBBY")
            updatePlayer(player_data['discordID'], "isAlive", True)
            logEvent(f"Moved {player} to LOBBY", status="Normal", traceback=None)

        elif type == "final ring": # Final Ring Movement
            new_vc = getVCs()['FINAL RING']
            new_vc = await bot.fetch_channel(new_vc)

            try:
                await nextcord.Member.move_to(user, new_vc)
            except: pass
            updatePlayer(player_data['discordID'], "currentRegion", "FINAL RING")
            logEvent(f"Moved {player} to FINAL RING", status="Normal", traceback=None)

        elif type == "death": # Death Movement
            logEvent(f"{player} killed", status="Normal", traceback=None)
            new_vc = getVCs()['DEAD']
            new_vc = await bot.fetch_channel(new_vc)

            try:
                await nextcord.Member.move_to(user, new_vc)
            except: pass
            updatePlayer(player_data['discordID'], "currentRegion", "DEAD")
            if readJsonFile("gamemode") == "BR": # If game mode is BR, set isAlive to False
                updatePlayer(player_data['discordID'], "isAlive", False)
            logEvent(f"Moved {player} to DEAD", status="Normal", traceback=None)

    except Exception as e: logEvent(f"Error in playerMover: {e}", status="Error", traceback=traceback.format_exc())

async def observerCheck(observed_name, closest_region): # Check if player is being
    try:
        observed = readJsonFile("currentObservations")
        print("OBSERVER CHECK STARTING")
        if len(observed) > 0: # If there are observations
            print("OBSERVATIONS FOUND")
            for observer, player in observed.items(): # {observer: player}
                print(f"Checking observer: {observer} observing {player}")
                if observer == observed_name:  # if observer is observing this player
                    player_data = getPlayer(observed_name)
                    observer_data = getPlayer(observer)
                    print("GOT OBSERVER AND PLAYER DATA")
                    if player_data is not None and observer_data is not None:
                        if closest_region != observer_data['currentRegion']:
                            print("MOVING OBSERVER")
                            print(f"closest_region: {closest_region}, observer_region: {observer_data['currentRegion']}")
                            await asyncio.create_task(playerMover(observer_data['inGameName'], movement=closest_region, delay=0))
                            updatePlayer(observer_data['inGameName'], "currentRegion", closest_region)
                            logEvent(f"Moved {observer_data['inGameName']} to {closest_region} (Observing {player_data['inGameName']})", status="Normal", traceback=None)

    except Exception as e: logEvent(f"Error in observerCheck: {e}", status="Error", traceback=traceback.format_exc())

async def eventHandler(event): # Handle events from LiveApex
    try:
        if event != None:
            #print(event)
            if 'category' in event:
                game_data.append(event)

                if event['category'] == "gameStateChanged":
                    if event['state'] == "Playing":
                        updateJsonFile("gameState", "Playing")
                        updateJsonFile("movementLocked", False) # Unlock movement

                        for player in getAllPlayers():
                            updatePlayer(player['inGameName'], "isAlive", True)
                        logEvent("Game Started", status="Normal", traceback=None)

                    elif event['state'] == "Resolution":
                        for player in getAllPlayers():
                            try:
                                await asyncio.create_task(playerMover(player['inGameName'], pos=None, type='lobby', delay=0))
                            except: pass
                            updatePlayer(player['inGameName'], "currentlyObserving", None) # Reset observation

                        updateJsonFile("gameState", None) # Reset game state
                        updateJsonFile("movementLocked", False) # Unlock movement
                        updateJsonFile("currentObservations", {}) # Clear observations
                        updateJsonFile("movementLocked", True) # Lock movement after lobby
                        logEvent("Game Ended, Moved all players to LOBBY and reset JSON to starting state", status="Normal", traceback=None)

                        await asyncio.sleep(7) # Wait for 7 seconds to ensure all other event threads are done
                        time = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
                        with open(f"Games/{time}.json", "a") as f: # Save game data to file
                            json.dump(game_data, f, indent=4)
                        game_data.clear()
                        logEvent(f"Game Data Saved: '{time}.json'", status="Normal", traceback=None)

                elif event['category'] == "matchSetup":
                    playlist = event['playlistName']
                    if playlist == "World's Edge" or playlist == "E-District":
                        updateJsonFile("gamemode", "BR")
                    elif playlist == "Team Deathmatch" or playlist == "Big Team Deathmatch":
                        updateJsonFile("gamemode", "TDM")
                    elif playlist == "Control":
                        updateJsonFile("gamemode", "Control")
                    elif playlist == "Gun Run":
                        updateJsonFile("gamemode", "Gun Run")
                    elif playlist == "Arenas":
                        updateJsonFile("gamemode", "Arenas")

                elif event['category'] == "ringFinishedClosing":
                    if event['stage'] == 3: # Ring 4 just closed -> move all to final ring vc as ring 5 countdown begins
                        for player in getAllPlayers():
                            if player['isAlive'] == True:
                                await asyncio.create_task(playerMover(player['inGameName'], pos=None, type='final ring', delay=0))

                        logEvent("Final Ring Countdown Started, Moved all players to FINAL RING", status="Normal", traceback=None)

                elif event['category'] in player_events_list: # if player appears in event
                    await asyncio.create_task(playerMover(event['player']['name'], event['player']['pos'], type="normal", delay=0))

                elif event['category'] in attacker_victim_list: # if attacker and victim appear in event
                    attacker = event['attacker']
                    victim = event['victim']

                    try: await asyncio.create_task(playerMover(attacker['name'], attacker['pos'], type="normal", delay=0)) # move attacker
                    except: pass # if attacker is world

                    if event['category'] == "playerKilled": # if victim is killed, move to dead
                        await asyncio.create_task(playerMover(victim['name'], victim['pos'], type="death", delay=3))

                    else: # if victim is not killed, move
                        await asyncio.create_task(playerMover(victim['name'], victim['pos'], type="normal", delay=0))

                elif event['category'] == "playerRevive":
                    player = event['player']
                    revived = event['revived']

                    player_data = getPlayer(player['name'])
                    if player_data != None:
                        await asyncio.create_task(playerMover(player['name'], player['pos'], type="normal", delay=0))
                    revived_data = getPlayer(revived['name'])
                    if revived_data != None:
                        await asyncio.create_task(playerMover(revived['name'], revived['pos'], type="normal", delay=0))

                    logEvent(f"{player['name']} revived {revived['name']}", status="Normal", traceback=None)

                elif event['category'] == "playerAssist":
                    player = event['player']
                    assistant = event['assistant']

                    player_data = getPlayer(player['name'])
                    if player_data != None:
                        await asyncio.create_task(playerMover(player['name'], player['pos'], type="normal", delay=0))

                    try:
                        assistant_data = getPlayer(assistant['name'])
                        if assistant_data != None:
                            await asyncio.create_task(playerMover(assistant['name'], assistant['pos'], type="normal", delay=0))
                    except: pass

                    logEvent(f"{assistant['name']} assisted {player['name']}", status="Normal", traceback=None)

                elif event['category'] == "playerRespawnTeam":
                    player = event['player']
                    respawnedTeammates = event['respawnedTeammates']

                    player_data = getPlayer(player['name'])
                    if player_data != None:
                        await asyncio.create_task(playerMover(player['name'], player['pos'], type="normal", delay=0))

                    for teammate in respawnedTeammates:
                        teammate_data = getPlayer(teammate['name'])
                        if teammate_data != None:
                            updatePlayer(teammate['name'], "isAlive", True)
                            await asyncio.create_task(playerMover(teammate['name'], teammate['pos'], type="normal", delay=0))
                            logEvent(f"{teammate['name']} was respawned by {player['name']}", status="Normal", traceback=None)

                elif event['category'] == "observerSwitched":
                    targetTeam = event['targetTeam']

                    for player in targetTeam:
                        player_data = getPlayer(player['name'])
                        if player_data != None:
                            await asyncio.create_task(playerMover(player['name'], player['pos'], type="normal", delay=0))

                    for player in getAllPlayers():
                        if player['inGameName'] == event['observer']['name']:
                            updatePlayer(event['observer']['name'], "currentlyObserving", event['target']['name']) # observer will now follow this player
                            await asyncio.create_task(playerMover(event['observer']['name'], getPlayer(event['target']['name'])['currentRegion'], delay=0)) # check/move to new player
                            observations = readJsonFile("currentObservations")
                            observer_name = event['observer']['name']
                            target_name = event['target']['name']
                            observations[observer_name] = target_name # add/update observer to current observations
                            updateJsonFile("currentObservations", observations)
                            logEvent(f"{event['observer']['name']} is now observing {event['target']['name']}", status="Normal", traceback=None)

    except Exception as e: logEvent(f"Error in event_handler: {e}", status="Error", traceback=traceback.format_exc())

game_data = []
async def filter_events(event):
    try:
        event_queue.put_nowait(event)
    except asyncio.QueueFull:
        formatOutput("Event queue full, dropping event", status="Warning", context="LiveApex")

async def event_worker():
    while True:
        event = await event_queue.get()
        try: await eventHandler(event)

        except Exception as e: logEvent(f"Error in event_worker: {e}", status="Error", traceback=traceback.format_exc())

        finally: event_queue.task_done()

async def scheduler_tasks():
    await load_map_cache()
    await load_player_cache()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(flush_map_cache, 'interval', seconds=30) # Flush map cache to json every 30 seconds
    scheduler.add_job(flush_player_cache, 'interval', seconds=20) # Flush player cache to json every 20 seconds
    scheduler.start()

async def main():
    scheduler_tasks_task = asyncio.create_task(scheduler_tasks())
    bot_task = asyncio.create_task(bot.start(BOT_TOKEN))

    api_task = asyncio.create_task(LiveApex.Core.startLiveAPI())
    listener_task = asyncio.create_task(LiveApex.Core.startListener(filter_events))
    workers = [asyncio.create_task(event_worker()) for _ in range(5)] # 5 working threads for processing events

    await asyncio.gather(scheduler_tasks_task, bot_task, api_task, listener_task, *workers)

asyncio.run(main())