### KEYS AND PASSWORDS FOR BOT ###
import pymongo, certifi
ca = certifi.where()

### EDIT TO INCLUDE REQUIRED INFORMATION ###
# DISCORD
BOT_TOKEN = "YOUR BOT TOKEN"

# MONGODB (DATABASE)
DB_PASSWORD = "YOUR DB PASSWORD"
DB_USERNAME = "YOUR DB USERNAME"
DB_STRING = "DB STRING AFTER <password> UP TO .net/ | @example.exmpl.mongodb.net/"
DB = pymongo.MongoClient(f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}{DB_STRING}?retryWrites=true&w=majority", tlsCAFile=ca)

# DGS TOKEN
DGS_TOKEN = "YOUR DGS TOKEN"