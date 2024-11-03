import os
import subprocess
import asyncio
import shutil

from asyncio import sleep
from datetime import datetime, timedelta
from pymongo.errors import DuplicateKeyError

from telethon import TelegramClient, errors
from telethon.tl.types import MessageMediaPhoto

from Emilia import API_HASH, API_ID, LOGGER, db, DEV_USERS, ORIGINAL_EVENT_LOOP, TOKEN, telethn
from Emilia.custom_filter import register
from Emilia.tele.backup import send

clone_db = db.clone
timer = db.timer
startpic = db.startpic
user_db = db.users
chat_db = db.chats

@register(pattern="stats")
async def stats_(event):
    if not event.sender_id in DEV_USERS:
        return await event.reply("Only my Arsh can use this command!")
    users = await db.users.count_documents({})
    chats = await db.chats.count_documents({})
    bots = await clone_db.count_documents({})
    message = f"**Chats**: {chats}\n**Users**: {users}\n**Cloned Bots Active**: {bots}"
    await event.reply(message)

async def run_cloned_bot(directory_path):
    try:
        LOGGER.error("Starting cloned bot")
        process = await asyncio.create_subprocess_exec(
            "python3", "-m", "Emilia",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=directory_path
        )
        stdout, stderr = await process.communicate()
        LOGGER.error(f"Cloned bot stdout: {stdout.decode()}")
        if process.returncode != 0:
            LOGGER.error(f"Cloned bot failed to start. Error: {stderr.decode()}")
        else:
            LOGGER.error("Cloned bot started successfully.")
    except Exception as e:
        LOGGER.error(f"Error occurred while running cloned bot: {e}")


async def get_bot_info(token, user_id):
    try:
        client = TelegramClient(f"{user_id}", API_ID, API_HASH)
        await client.start(bot_token=token)
        bot = await client.get_me()
        return bot.id, bot.username, bot.first_name
    except errors.AccessTokenExpiredError:
        await delete_clone(user_id)
        return "expired", None, None
    except Exception as e:
        LOGGER.error(f"An error occurred while getting bot info: {e}")
        return None, None, None

config = """
import json
import os


def get_user_list(config, key):
    with open("{}/Emilia/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


class Config(object):
    API_HASH = "45a20dd93a6d"
    API_ID = 61

    BOT_ID = {}
    BOT_USERNAME = "{}"

    MONGO_DB_URL = "mongodb://arsnnection=true&authSource=admin"

    SUPPORT_CHAT = "SpiralTechDivision"
    UPDATE_CHANNEL = "SpiralUpdates"
    START_PIC = "{}"
    DEV_USERS = [6040984893]
    TOKEN = "{}"

    EVENT_LOGS = -100
    OWNER_ID = 6040984893

    TEMP_DOWNLOAD_DIRECTORY = "./"
    BOT_NAME = "{}"
    WALL_API = "gay"
    ORIGINAL_EVENT_LOOP = False


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True

"""


async def clone(user_id, token):
    await sleep(5)
    LOGGER.error(f"Waiting for 5 seconds before creating bot for user {user_id}")
    directory_path = "/app" + f"/Emilia-{user_id}"

    LOGGER.error(f"Cloning the repository for user {user_id}")
    git_repo_url = "https://github.com/ArshCypherZ/Emilia.git"
    try:
        subprocess.run(["git", "clone", git_repo_url, directory_path])
    except Exception as e:
        LOGGER.error(f"An error occurred while cloning the repository: {e}")
        LOGGER.error("Pulling the repository instead")
        os.chdir(directory_path)
        subprocess.run(["git", "pull"])
        
    LOGGER.error(f"Cloned the repository for user {user_id}")
    file_path = f"{directory_path}/Emilia/config.py"

    bot_id, bot_username, bot_name = await get_bot_info(token, user_id)
    if not (bot_id and bot_username and bot_name):
        bot_id = 5737513498
        bot_username = "Elf_Robot"
        bot_name = "Emilia"
    if bot_id == "expired":
        return
    
    mm = await startpic.find_one({"token": TOKEN})
    if mm:
        url = mm["url"]
    else:
        url = "https://pic-bstarstatic.akamaized.net/ugc/9e98b6c8872450f3e8b19e0d0aca02deff02981f.jpg@1200w_630h_1e_1c_1f.webp"

    try:
        with open(file_path, "w") as file:
            file.write(config.format("", "", bot_id, bot_username, url, token, bot_name))
    except:
        return
    LOGGER.error("Wrote the token to config.py")

    LOGGER.error("Running the bot")
    os.chdir(directory_path)
    await run_cloned_bot(directory_path)
    LOGGER.error("Ran the bot")


async def clone_start_up():
    all_users = await clone_db.find({}).to_list(length=None)
    tasks = []
    backup = asyncio.create_task(send())
    tasks.append(backup)
    started_clones = set()
    for index, user in enumerate(all_users):
        user_id = user["_id"]
        if user_id not in started_clones:
            token = user["token"]
            delay = index * 20
            task = asyncio.create_task(clone_with_delay(user_id, token, delay))
            tasks.append(task)
            started_clones.add(user_id)
    await asyncio.gather(*tasks)

async def clone_with_delay(user_id, token, delay):
    await asyncio.sleep(delay)
    await clone(user_id, token)

@register(pattern="clone")
async def clone_bot(event):
    if not ORIGINAL_EVENT_LOOP:
        return await event.reply("This feature is only available for original bot.")
    if not event.is_private:
        return await event.reply("Please clone **Emilia** in your private chat.")
    user_id = event.sender_id
    check = await clone_db.find_one({"_id": user_id})
    if check:
        return await event.reply(
            "You have already cloned **Emilia**. If you want to delete the clone, use `/deleteclone <bottoken>`"
        )
    if len(event.text.split()) == 1:
        return await event.reply(
            "Please provide the bot token from @BotFather in order to clone **Emilia**.\n**Example**: `/clone 219218219:jksswq`"
        )
    token = event.text.split(None, 1)[1]
    check_token = await clone_db.find_one({"token": token})
    if check_token:
        return await event.reply("The same bot token has been used to clone **Emilia**. Please use a different bot token.")
    time = await timer.find_one({"_id": user_id})
    if time:
        if (datetime.now() - time["time"]) < timedelta(hours=13):
            return await event.reply("You have recently deleted the cloned **Emilia**. Please wait for 12 hours before cloning again.")
    wait = await event.reply("Cloning the bot. Please wait...")
    try:
        try:
            client = TelegramClient(f"gay-{user_id}", API_ID, API_HASH)
            await client.start(bot_token=token)
        except errors.AccessTokenExpiredError:
            await wait.delete()
            await event.reply("The bot token you provided is expired. Please provide the correct bot token.")
            return
        except errors.AccessTokenInvalidError:
            await wait.delete()
            await event.reply("The bot token you provided is invalid. Please provide the correct bot token. Perhaps you forgot to remove [] or <> around the token?")
            return
        except errors.FloodWaitError as e:
            LOGGER.error(f"An error occurred while testing the token: {e}")
            await wait.delete()
            await event.reply("You have been spamming the bot token. Please try again later.")
            return
        except Exception as e:
            LOGGER.error(f"An error occurred while testing the token: {e}")
            await wait.delete()
            await event.reply("The bot token you provided is incorrect. Please provide the correct bot token. If the token is correct, please wait a while and try again later (12 hours approximately). If the issue persists, contact @SpiralTechDivision")
            return
        await clone_db.insert_one({"_id": user_id, "token": token})
        k = await event.reply(
            "Cloned **Emilia** successfully. Running the bot in few minutes.\n\nIf you want to delete the bot, use `/deleteclone <bottoken>`.\n\n**NOTE**: The bot will get restarted every 12 hours."
        )
        try:
            await clone(user_id, token)
        except Exception as e:
            LOGGER.error(f"An error occured while cloning Emilia: {e}")
            await clone_db.delete_many({"_id": user_id})
            await event.reply(f"An error occurred while cloning **Emilia**. Please try again or contact support @SpiralTechDivision.")
            await k.delete()
            await wait.delete()
            return
    except Exception as e:
        LOGGER.error(f"An error occured while cloning: {e}")
        await clone_db.delete_many({"_id": user_id})
        await event.reply(f"An error occurred while cloning **Emilia**. Please try again or contact support @SpiralTechDivision.")
    await wait.delete()

async def delete_folder(folder_path):
    for path, subdirs, files in os.walk(folder_path, topdown=False):
        for name in files:
            os.remove(os.path.join(path, name))
        for name in subdirs:
            shutil.rmtree(os.path.join(path, name))
    os.rmdir(folder_path)

@register(pattern="deleteclone")
async def delete_cloned(event):
    if not ORIGINAL_EVENT_LOOP:
        return await event.reply("This feature is only available in original bot.")
    if not event.is_private:
        return await event.reply("Please delete Emilia's clone in your private chat.")
    user_id = event.sender_id
    check = await clone_db.find_one({"_id": user_id})
    if not check:
        return await event.reply(
            "You have not cloned **Emilia** yet. If you want to clone it, use `/clone <bottoken>`"
        )
    if len(event.text.split()) == 1:
        return await event.reply(
            "Please provide the bot token from @BotFather in order to delete the cloned **Emilia**. Example: `/deleteclone 219218219:jksswq`"
        )
    token = event.text.split(None, 1)[1]
    if check["token"] != token:
        return await event.reply(
            "The bot token you provided is incorrect. Please provide the correct bot token."
        )
    await clone_db.delete_many({"_id": user_id})
    await delete_folder(f"/app/Emilia-{user_id}")
    await timer.insert_one({"_id": user_id, "time": datetime.now()})
    
    await event.reply(
        "Deleted the cloned bot successfully. Within 12 hours, the bot will be stopped."
    )


async def delete_clone(user_id):
    await clone_db.delete_many({"_id": user_id})
    await delete_folder(f"/app/Emilia-{user_id}")
    try:
        await timer.insert_one({"_id": user_id, "time": datetime.now()})
    except DuplicateKeyError:
        LOGGER.error(f"Duplicate entry for user {user_id}.")
        pass
    LOGGER.error(f"Deleted the cloned bot for user {user_id} successfully.")


@register(pattern="setstartpic")
async def set_startpic(event):
    if ORIGINAL_EVENT_LOOP:
        return await event.reply("This feature is only available in cloned bots. Learn more about cloning Emilia by using `/help Clone`.")
    get_info = await clone_db.find_one({"_id": event.sender_id})
    if not get_info:
        return await event.reply("You have not cloned **Emilia** yet. If you want to clone it, use `/clone <bottoken>` in @Elf_Robot private chat.")
    if not event.is_private:
        return await event.reply("Please set the start picture of your clone in bot's private chat.")
    if get_info["token"] != TOKEN:
        return await event.reply("Only the one who made the clone bot can set the start pic.")

    if len(event.text.split()) == 1:
        return await event.reply(
            "Please provide the image url in order to set the start pic. Example: `/setstartpic https://example.com/image.jpg`\nIf you do not know how to get the image url, send the image and reply it with `/tgm` to get the image url."
        )
    url = event.text.split(None, 1)[1]
    if not url.endswith((".jpg", ".jpeg", ".png")):
        return await event.reply("The url you provided is not an image url. Please provide a valid image url. It should end with `.jpg`, `.jpeg` or `.png`.")
    await startpic.update_one({"token": TOKEN}, {"$set": {"url": url}}, upsert=True)
    await event.reply("Start pic set successfully. The start pic will be updated in your clone within 12 hours.")


@register(pattern="broadcast")
async def broadcast(event):
    user_id = event.sender_id
    get_info = await clone_db.find_one({"_id": user_id})
    if not get_info:
        return await event.reply("You have not cloned **Emilia** yet. If you want to clone it, use `/clone <bottoken>` in @Elf_Robot private chat.")
    if not event.is_private:
        return await event.reply("Please broadcast in your clone's private chat.")
    if get_info["token"] != TOKEN:
        return await event.reply("Only the one who made the clone bot can broadcast messages.")
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("Please reply to a message to broadcast.")
    text = event.text.split(None, 1)[1]
    if not text:
        return await event.reply("Please provide the flag to broadcast the message. Example: `/broadcast -all` or `/broadcast -users` or `/broadcast -chats`")
    if text == "-all":
        await user_broadcast(event, reply)
        await chat_broadcast(event, reply)
    elif text == "-users":
        await user_broadcast(event, reply)
    elif text == "-chats":
        await chat_broadcast(event, reply)
    else:
        await event.reply("Invalid flag. Use `/broadcast -all` or `/broadcast -users` or `/broadcast -chats`")

async def user_broadcast(event, reply):
    async for user in user_db.find({}):
        try:
            await telethn.forward_messages(user["user_id"], reply)
        except errors.FloodWaitError as e:
            await sleep(e.seconds)
            continue
        except Exception as e:
            pass
    await event.reply("Broadcasted the message to all users successfully.")

async def chat_broadcast(event, reply):
    async for chat in chat_db.find({}):
        try:
            await telethn.forward_messages(chat["chat_id"], reply)
        except errors.FloodWaitError as e:
            await sleep(e.seconds)
            continue
        except Exception as e:
            pass
    await event.reply("Broadcasted the message to all chats successfully.")
