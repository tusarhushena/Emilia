import asyncio
import importlib
import traceback
import os
from os.path import dirname
from sys import platform

import uvloop
from pyrogram import idle

from Emilia import LOGGER, anibot, create_indexes, pgram, telethn, ORIGINAL_EVENT_LOOP, db, start_session
from Emilia.info import ALL_MODULES
from Emilia.tele.clone import clone_start_up

HELP_MSG = "Click the button below to get help menu in your pm ~"
START_MSG = "**Hie Senpai ~ UwU** I am well and alive ;)"

HELP_IMG = "https://images-cdn.9gag.com/photo/aXvvrdz_700b.jpg"
START_IMG = "https://image.myanimelist.net/ui/5LYzTBVoS196gvYvw3zjwNzKv3dEGU_pTR8jQb-vfgTLHxH8jxREmQF_Ct58ke7N"

IMPORTED = {}
HELPABLE = {}
SUB_MODE = {}
HIDDEN_MOD = {}

USER_INFO = []

cdir = dirname(__file__)
if platform == "linux" or platform == "linux2":
    path_dirSec = "/"
elif platform == "win32":
    path_dirSec = "\\"


for mode in ALL_MODULES:
    module = mode.replace(cdir, "").replace(path_dirSec, ".")
    imported_module = importlib.import_module("Emilia" + module)

    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__sub_mod__") and imported_module.__sub_mod__:
        SUB_MODE[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__hidden__") and imported_module.__hidden__:
        HIDDEN_MOD[imported_module.__mod_name__.lower()] = imported_module.__hidden__

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)


async def start_anibot():
    await anibot.start()

async def start_pgram():
    uvloop.install() # Comment it if using Windows
    await pgram.start()
    await idle()

async def gae():
    tasks = [start_anibot(), start_pgram()]
    await create_indexes()
    await start_session()
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        if ORIGINAL_EVENT_LOOP: # Main Bot
            os.chdir("/app") # Change to your directory where the bot is located on the server
            asyncio.get_event_loop().run_until_complete(asyncio.gather(clone_start_up(), gae()))
        else:
            asyncio.get_event_loop().run_until_complete(gae()) # Clone Bot
        telethn.run_until_disconnected()
    except KeyboardInterrupt:
        pass
    except Exception:
        err = traceback.format_exc()
        LOGGER.error(err)
    finally:
        asyncio.get_event_loop().stop()
        LOGGER.error("Stopped Services.")
