import json
import os


def get_user_list(config, key):
    with open("{}/Emilia/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


class Config(object):
    API_HASH = "125c7cf7edc8c0474a0be891eaf69d6c" # API_HASH from my.telegram.org
    API_ID = 22273859 # API_ID from my.telegram.org

    BOT_ID = 7741293072 # BOT_ID
    BOT_USERNAME = "HarryCloneBot" # BOT_USERNAME

    MONGO_DB_URL = "mongodb+srv://tusar:tusar1@cluster0.guw5d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    SUPPORT_CHAT = "DeadlineTechSupport" # Support Chat Username
    UPDATE_CHANNEL = "DeadlineTechTeam" # Update Channel Username
    START_PIC = "https://files.catbox.moe/ka9qcw.jpg" # Start Image
    DEV_USERS = [6848223695, 7186437295, 7765692814] # Dev Users
    TOKEN = "7741293072:AAEc9F4Oy8ShJtQBOWn4LyM1p08DgNhlCMk" # Bot Token from @BotFather
    CLONE_LIMIT = 200 # Number of clones your bot can make

    EVENT_LOGS = -1002408792676 # Event Logs Chat ID
    OWNER_ID = 6848223695 # Owner ID
 
    TEMP_DOWNLOAD_DIRECTORY = "./" # Temporary Download Directory
    BOT_NAME = "Harry Cloner" # Bot Name
    WALL_API = "6950f53" # Wall API from wall.alphacoders.com
    ORIGINAL_EVENT_LOOP = True # Do not Change


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
