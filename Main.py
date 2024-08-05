import datetime
import requests
import asyncio
import math
import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from BotData.colors import *
from BotData.mapdata import MapData
from Keyss import *

# Command List
command_list = ["start_session", "end_session", "link", "unlink_all"]

# Discord Vars
intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)

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

### Handy Functions
def getAllIDs(): # Get all VC IDs
    data = DB.Main.IDs.find_one({"vcCatergory": {"$exists": True}})
    return data

def getGameData(): # Get Game Data
    data = DB.Main.GameData.find_one({"map": {"$exists": True}})
    return data

def getAllPlayerData(): # Get All Player Data
    data = list(DB.Main.PlayerData.find())
    return data

def getPlayerData(player_name): # Get Single Player Data
    data = DB.Main.PlayerData.find_one({"IGN": player_name})
    return data

async def updatePresence(status): # Update Bot Presence
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

# Database
formatOutput("Connecting To Database...", status="Normal", context="STARTUP")
try:
    DB.admin.command('ping')
    formatOutput("Connected to Database", status="Good", context="STARTUP")
except Exception as e:
    formatOutput("Failed to Connect to Database", status="Error", context="STARTUP")

formatOutput("Connecting to Discord...", status="Normal", context="STARTUP")

@bot.event
async def on_ready():
    startup_time = round((datetime.datetime.now() - start_time).total_seconds() * 1000)
    formatOutput(f"{bot.user.name} has connected to Discord (Took {startup_time}ms)", status="Good", context="STARTUP")

    await startScheduler()

    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="for /start_session"))
    formatOutput("---------------------------------", status="Normal", context="STARTUP")

##### Logic
async def playerKilled(name): # Player Killed
    data = getPlayerData(name)
    if data != None: # Player is in DB
        if data['healthState'] == "Dead": return
        DB.Main.PlayerData.update_one({"IGN": name}, {"$set": {"healthState": "Dead"}})
        asyncio.create_task(userMover(name, movement="DEAD"))

async def playerMoved(player, pos): # Player Moved
    player_data = getPlayerData(player)
    if player_data != None: # Player is in DB
        player_poi = player_data['currentPOI']

        closest_poi = getClosestPOI(pos)
        if player_poi != closest_poi[0]: # Player is not in closest POI
            asyncio.create_task(userMover(player, movement=closest_poi[0]))

async def gameEnded(entry): # Game Ended
    formatOutput("Game Ended, returning players to lobby", status="Normal", context="API")
    DB.Main.GameData.update_one({"map": entry['map']}, {"$set": {"status": "Lobby"}})
    for player in getAllPlayerData():
        asyncio.create_task(userMover(player['IGN'], movement="LOBBY"))

async def apiCaller(): # Call API
    try:
        if getGameData() == None: # No game session started
            formatOutput("No Game Session Started", status="Warning", context="API")
            with open("log.txt", "a") as file:
                file.write(f"{datetime.datetime.now()} || No Game Session Started\n")
            return

        url = f"https://dgs-grace-prd.apexlegendsstatus.com/liveData?token={DGS_TOKEN}"
        response = requests.get(url)
        json_output = response.json()
        formatOutput(f"API CALLED", status="Normal", context="API")

        if 'error' not in json_output.keys(): # No Error
            with open("log.txt", "a") as file:
                file.write(f"{datetime.datetime.now()} || RAW API DATA: {json_output}\n")
            try:
                players = json_output['payload']['players']

                for player_id, player_data in players.items():
                    try:
                        try:
                            if player_data['teamName'] == "Spectator": continue # Ignore Spectators
                        except: continue

                        state = player_data['state']
                        name = player_data['name']
                        if state == "KILLED":
                            asyncio.create_task(playerKilled(name))

                        else:
                            position = player_data['pos']
                            asyncio.create_task(playerMoved(player=name, pos=position))
                            print(f"Player Name: {name}, Position: {position}, Status: {state}")

                    except Exception as e:
                        formatOutput(f"Error while processing player data, Error: {e} {player_data}", status="Error", context="API")
                        continue

            except Exception as e:
                formatOutput(f"JSON Error: {e} {json_output}", status="Error", context="API")

        else:
            if getGameData()['status'] != "Lobby": asyncio.create_task(gameEnded(entry=getGameData()))
            else: formatOutput(f"   No game is running", status="Warning", context="API")
            with open("log.txt", "a") as file:
                file.write(f"{datetime.datetime.now()} || No game is running\n")

    except Exception as e:
        if response.status_code == 200: pass # DGS Live API will output 200 IF no game is running & IF the API has responded with a ~'no game running' within the last 60sec
        else: formatOutput(f"Recieved invaild status code Error: {response.status_code}\n{e}", status="Error", context="API")

async def userMover(player_name, movement): # Move user to VC
    try:
        IDs = getAllIDs()
        player_data = getPlayerData(player_name)

        guild = bot.get_guild(1165569173880049664)
        user = guild.get_member(player_data['discordID'])

        new_vc = IDs['vcList'][movement]
        new_vc = await bot.fetch_channel(new_vc)
        DB.Main.PlayerData.update_one({"IGN": player_name}, {"$set": {"currentPOI": movement}})

        await nextcord.Member.move_to(user, new_vc)

    except Exception as e:
        if "Target user is not connected to voice" in str(e): formatOutput(f"{player_name} is not connected to voice", status="Warning", context="User Mover")
        else: formatOutput(f"Error while moving user, Error: {e}", status="Error", context="User Mover")

def getClosestPOI(player_pos): # Calculate closest POI to player
    player_x = player_pos['x']
    player_y = player_pos['y']

    pois = MapData[getGameData()['map']]

    distances = {}
    for poi_name, poi_info in pois.items():
        poi_x = poi_info['POICenter'][0]
        poi_y = poi_info['POICenter'][1]
        distance = math.sqrt((player_x - poi_x)**2 + (player_y - poi_y)**2)
        distances[poi_name] = distance

    sorted_distances = sorted(distances.items(), key=lambda item: item[1])
    print(sorted_distances)

    function_output = [sorted_distances[0][0], sorted_distances[0][1]]
    print(f"OUTPUT: {function_output}")

    return function_output

async def startScheduler():
    try:
        formatOutput("Starting Scheduler...", status="Normal", context="STARTUP")
        scheduler = AsyncIOScheduler()
        scheduler.add_job(apiCaller, 'cron', second='*/7') # Every 7 seconds
        scheduler.start()
        formatOutput("Scheduler Started", status="Good", context="STARTUP")

    except Exception as e:
        formatOutput(f"Something went wrong while starting scheduler. Error: {e}", status="Error", context="STARTUP")

bot.run(BOT_TOKEN)