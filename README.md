# Apex Proximity Chat
A crude implementation of proximity chat for Apex Legends.\
**This will only work within custom games, public/ranked games will not work.**\
Whenever a player does an action their location is checked and moves the player to a new VC if they have changed closest POI.\
One VC per POI, so anyone can communicate with anyone in the same POI. Some sub POIs have been added to fill the gaps between POIs.

## Information
What is the 'Cell Tower Method'? ---------------->> [FIND OUT](https://github.com/CatotronExists/Apex-Prox-Chat/wiki/Cell-Tower-Method)

# v2 (W.I.P)
Migrated from using DGS API to use LiveApex. Lowering the delay between in game actions to moving players to different VCs.\

# Requirements
<details>
  <summary>Installing Python</summary>

You can install python from the [official website](https://www.python.org/downloads/).
Make sure to check the box that says "Add Python to PATH" during installation.

To install the required packages, open the command prompt and type any commands that start with ```pip install```.

</details>

Python 3.12 or higher

LiveApex ```pip install LiveApex```
Nextcord ```pip install nextcord```

Include ```+cl_liveapi_enabled 1``` in your steam launch options for Apex Legends.

# Setup Guide
0. Install the requirements listed above.
1. Create a new Discord bot application [here](https://discord.com/developers/applications). Once created, go to the "Bot" tab and click "Reset Token" to generate a new token. Copy this token, and paste it into `Keys.py` under `BOT_TOKEN`.
2. In the "Installation" tab, add "bot" to the Guild Install. Then add "Administrator" permissions to the bot. This will allow the bot to manage voice channels and roles.
3. Download the latest release from the [releases page](https://github.com/CatotronExists/Apex-Prox-Chat/releases)
4. Run `Main.py`. The bot should start up, run `/start_session`, get all participants to link with `/link`, join the "LOBBY" voice channel, and start playing!

*To change map, run `/end_session` and `/start_session` again.*

# Credits
Created by Catotron | Discord Bot built with [Nextcord](https://github.com/nextcord/nextcord) | Powered by [LiveApex](https://github.com/CatotronExists/LiveApex)