# Apex Proximity Chat
A crude implementation of proximity chat for Apex Legends.\
**This will only work within custom games, public/ranked games will not work.**\
Whenever a player does an action their location is checked and moves the player to a new VC if they have changed region.\
One VC per region, so anyone can communicate with anyone in the same region.
This will work with any team type, but team members may not be in the same VC as each other.

# v2
Migrated from using DGS API to use LiveApex. Lowering the delay between in game actions to moving players to different VCs.\
Moved to using a json file to store data, rather than a database. Making it super easy to setup and run your own proximity chat server.\
Instead of using a simple radius check for POIs, proximity chat now uses predefined regions to determine which VC to move players to. This allows for more accurate placement of players in the correct VC based on their location in the game.

# Requirements
<details>
  <summary>Installing Python</summary>

You can install python from the [official website](https://www.python.org/downloads/).
Make sure to check the box that says "Add Python to PATH" during installation.

To install the required packages, open the command prompt and type any commands that start with ```pip install```.

</details>

Python 3.12 or higher

LiveApex ```pip install LiveApex```\
Nextcord 2.6.0 ```pip install nextcord==2.6.0```

Include ```+cl_liveapi_enabled 1``` & ```+cl_liveapi_ws_servers "ws://127.0.0.1:7777"``` in your steam launch options for Apex Legends.

# Setup Guide
0. Install the requirements listed above.
1. Create a new Discord bot application [here](https://discord.com/developers/applications). Once created, go to the "Bot" tab and click "Reset Token" to generate a new token. Copy this token, and paste it into `Keys.py` under `BOT_TOKEN`.
2. In the "Installation" tab, add "bot" to the Guild Install. Then add "Administrator" permissions to the bot. This will allow the bot to manage voice channels and roles.
3. Download the latest release from the [releases page](https://github.com/CatotronExists/Apex-Prox-Chat/releases)
4. Run `Main.py`. The bot should start up, run `/start_session`, get all participants to link with `/link`, join the "LOBBY" voice channel, and start playing!

*The host must be in observer for this to work, host is not able to play*\
*Note: The regions are estimated to be slightly off, by a maximum of 5-8 meters. This is likely unoticable by players*

# General Player Guide
1. Link your discord account to your apex account by running `/link`.
2. Join the "LOBBY" voice channel.
(It is really that easy!)

No use of in game communication is allowed, (aside from pings) as this ruins the whole point.\
It is recommended to enable streamer mode in discord to disable the VC join/leave notifications.\
Console discord users may be disconnected from voice channels regularly (due to console jank), for these players it is recommended to instead use mobile versions of discord

# Credits
Created by Catotron | Discord Bot built with [Nextcord](https://github.com/nextcord/nextcord) | Powered by [LiveApex](https://github.com/CatotronExists/LiveApex)
