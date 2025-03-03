import json
import os


def get_user_list(config, key):
    with open("{}/Emilia/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


class Config(object):
    API_HASH = "9a098f01aa56c836f2e34aee4b7ef963" # API_HASH from my.telegram.org
    API_ID = 24620300 # API_ID from my.telegram.org

    BOT_ID = 7741293072 # BOT_ID
    BOT_USERNAME = "HarryCloneBot" # BOT_USERNAME

    MONGO_DB_URL = "mongodb+srv://botmaker9675208:botmaker9675208@cluster0.sc9mq8b.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" # MongoDB URL from MongoDB Atlas

    SUPPORT_CHAT = "DeadlineTechSupport" # Support Chat Username
    UPDATE_CHANNEL = "DeadlineTechTeam" # Update Channel Username
    START_PIC = "https://pic-bstarstatic.akamaized.net/ugc/9e98b6c8872450f3e8b19e0d0aca02deff02981f.jpg@1200w_630h_1e_1c_1f.webp" # Start Image
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
