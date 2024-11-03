import logging

import uvloop
from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from motor import motor_asyncio
from pyrogram import Client
from telethon import TelegramClient

from Emilia.config import Development as Config

# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

LOGGER = logging.getLogger(__name__)


TOKEN = Config.TOKEN
OWNER_ID = int(Config.OWNER_ID)
DEV_USERS = {int(x) for x in Config.DEV_USERS or []}
EVENT_LOGS = Config.EVENT_LOGS
API_ID = Config.API_ID
API_HASH = Config.API_HASH
MONGO_DB_URL = Config.MONGO_DB_URL
SUPPORT_CHAT = Config.SUPPORT_CHAT
BOT_USERNAME = Config.BOT_USERNAME
UPDATE_CHANNEL = Config.UPDATE_CHANNEL
START_PIC = Config.START_PIC

DEV_USERS.add(OWNER_ID)

scheduler = AsyncIOScheduler()

# Credits Logger
print("[Emilia] Emilia Is Starting. | Spiral Tech Project | Licensed Under MIT.")
plugins = dict(root="Emilia/anime")
pyro_plugins = dict(root="Emilia/pyro")

print("[INFO]: INITIALZING AIOHTTP SESSION")
async def start_session():
    global session
    session = ClientSession()


mongo = motor_asyncio.AsyncIOMotorClient(MONGO_DB_URL)
db = mongo["Emilia"]


async def create_indexes():
    users_collection = db.chatlevels
    userchat = db.users
    chatuser = db.chats
    floodmsg = db.flood_msgs
    userchat_def = [
        ("user_id", 1),
        ("username", 1),
        ("chats", 1),
        ("first_found_date", 1),
    ]
    chatuser_def = [("chat_id", 1), ("chat_title", 1), ("first_found_date", 1)]
    index_definition = [("points", -1), ("user_id", 1), ("chat_id", 1)]
    floodmsg_def = [("chat_id", 1), ("user_id", 1), ("msg_id", 1)]
    await users_collection.create_index(index_definition)
    await userchat.create_index(userchat_def)
    await chatuser.create_index(chatuser_def)
    await floodmsg.create_index(floodmsg_def)


DEV_USERS = list(DEV_USERS)

TRIGGERS = ("/ !").split()
ANILIST_CLIENT = 10061
ANILIST_SECRET = "NTRAM29JYsTVMYphFkLd9meMoPByxB38aBGDWkyg"
ANILIST_REDIRECT_URL = "https://anilist.co/api/v2/oauth/pin"


DOWN_PATH = "Emilia/anime/downloads/"
HELP_DICT = dict()


HELP_DICT[
    "Group"
] = """
Group based commands:
/anisettings - Toggle stuff like whether to allow 18+ stuff in group or whether to notify about aired animes, etc and change UI
/anidisable - Disable use of a cmd in the group (Disable multiple cmds by adding space between them)
`/anidisable anime anilist me user`
/anienable - Enable use of a cmd in the group (Enable multiple cmds by adding space between them)
`/anienable anime anilist me user`
/anidisabled - List out disabled cmds
"""

HELP_DICT[
    "Additional"
] = """Use /anireverse cmd to get reverse search via tracemoepy API
__Note: This works best on uncropped anime pic,
when used on cropped media, you may get result but it might not be too reliable__
Use /schedule cmd to get scheduled animes based on weekdays
Use /watch cmd to get watch order of searched anime
Use /fillers cmd to get a list of fillers for an anime
Use /quote cmd to get a random quote
"""

HELP_DICT[
    "Anilist"
] = """
Below is the list of basic anilist cmds for info on anime, character, manga, etc.
/anime - Use this cmd to get info on specific anime using keywords (anime name) or Anilist ID
(Can lookup info on sequels and prequels)
/anilist - Use this cmd to choose between multiple animes with similar names related to searched query
(Doesn't includes buttons for prequel and sequel)
/character - Use this cmd to get info on character
/manga - Use this cmd to get info on manga
/airing - Use this cmd to get info on airing status of anime
/top - Use this cmd to lookup top animes of a genre/tag or from all animes
(To get a list of available tags or genres send /gettags or /getgenres
'/gettags nsfw' for nsfw tags)
/user - Use this cmd to get info on an anilist user
/browse - Use this cmd to get updates about latest animes
"""

HELP_DICT[
    "Oauth"
] = """
This includes advanced anilist features
Use /auth or !auth cmd to get details on how to authorize your Anilist account with bot
Authorising yourself unlocks advanced features of bot like:
- adding anime/character/manga to favourites
- viewing your anilist data related to anime/manga in your searches which includes score, status, and favourites
- unlock /flex, /ame, /activity and /favourites commands
- adding/updating anilist entry like completed or plan to watch/read
- deleting anilist entry
Use /flex or !flex cmd to get your anilist stats
Use /logout or !logout cmd to disconnect your Anilist account
Use /ame or !ame cmd to get your anilist recent activity
Can also use /activity or !activity
Use /favourites or !favourites cmd to get your anilist favourites
"""


TEMP_DOWNLOAD_DIRECTORY = Config.TEMP_DOWNLOAD_DIRECTORY
WALL_API = Config.WALL_API
BOT_ID = Config.BOT_ID
BOT_NAME = Config.BOT_NAME
ORIGINAL_EVENT_LOOP = Config.ORIGINAL_EVENT_LOOP

uvloop.install() # Comment it if using Windows
if ORIGINAL_EVENT_LOOP:
    pgram = Client("pgram", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN, plugins=pyro_plugins, workers=32, sleep_threshold=0) # Set workers to 32 if you have a powerful server
else:
    pgram = Client("pgram", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN, plugins=pyro_plugins)
telethn = TelegramClient("telethn", API_ID, API_HASH, flood_sleep_threshold=0).start(bot_token=TOKEN)
anibot = Client("anibot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN, sleep_threshold=0, plugins=plugins)
