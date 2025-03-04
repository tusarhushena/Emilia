import os
import subprocess
import asyncio
import shutil

from datetime import datetime
from pymongo.errors import DuplicateKeyError

from telethon import TelegramClient, errors

from Emilia import API_HASH, API_ID, LOGGER, db, DEV_USERS, ORIGINAL_EVENT_LOOP, TOKEN, telethn, CLONE_LIMIT, SUPPORT_CHAT
from Emilia.custom_filter import register

# Database collections
clone_db = db.clone
timer = db.timer
user_db = db.users
chat_db = db.chats

CONFIG_TEMPLATE = """API_ID = {api_id}
API_HASH = "{api_hash}"
BOT_ID = {bot_id}
BOT_USERNAME = "{bot_username}"
BOT_TOKEN = "{bot_token}"
BOT_NAME = "{bot_name}"
"""

@register(pattern="stats")
async def stats_(event):
    if event.sender_id not in DEV_USERS:
        return await event.reply("Only my Developer can use this command!")
    users = await db.users.count_documents({})
    chats = await db.chats.count_documents({})
    bots = await clone_db.count_documents({})
    message = f"**Chats**: {chats}\n**Users**: {users}\n**Cloned Bots Active**: {bots}"
    await event.reply(message)

async def run_and_restart_cloned_bot(directory_path):
    """
    Restart cloned bot every 12 hours.
    """
    while True:
        LOGGER.error("Starting cloned bot from: " + directory_path)
        process = await asyncio.create_subprocess_exec(
            "python3", "-m", "Emilia",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=directory_path
        )
        try:
            await asyncio.wait_for(process.wait(), timeout=43200)  # 12 hours
        except asyncio.TimeoutError:
            LOGGER.error("12 hours passed, restarting cloned bot...")
            process.kill()
            await process.wait()
        stdout, stderr = await process.communicate()
        LOGGER.error(f"Cloned bot stdout: {stdout.decode()}")
        if process.returncode != 0:
            LOGGER.error(f"Cloned bot error: {stderr.decode()}")
        LOGGER.error("Restarting cloned bot in 5 seconds...")
        await asyncio.sleep(5)

async def get_bot_info(token, user_id):
    if not isinstance(API_ID, int) or not isinstance(API_HASH, str):
        LOGGER.error("Invalid API_ID or API_HASH format. Please check your config.")
        return None, None, None

    try:
        client = TelegramClient(f"{user_id}", API_ID, API_HASH)
        await client.start(bot_token=token)
        bot = await client.get_me()
        await client.disconnect()
        return bot.id, bot.username, bot.first_name
    except errors.ApiIdInvalidError:
        LOGGER.error("API_ID or API_HASH is invalid. Please check your credentials.")
        return None, None, None
    except errors.AccessTokenExpiredError:
        await delete_clone(user_id)
        return "expired", None, None
    except Exception as e:
        LOGGER.error(f"An error occurred while getting bot info: {e}")
        return None, None, None

async def clone_start_up():
    """
    On main bot startup, iterate over saved clones and start each one.
    """
    all_users = await clone_db.find({}).to_list(length=None)
    tasks = []
    backup = asyncio.create_task(send())
    tasks.append(backup)
    for index, user in enumerate(all_users):
        user_id = user["_id"]
        token = user["token"]
        delay = index * 5  # A small delay for faster overall startup
        task = asyncio.create_task(clone_with_delay(user_id, token, delay))
        tasks.append(task)
    await asyncio.gather(*tasks)

async def clone_with_delay(user_id, token, delay):
    await asyncio.sleep(delay)
    await clone(user_id, token)

async def clone(user_id, token):
    """
    Clones a bot and starts it.
    """
    if not isinstance(API_ID, int) or not isinstance(API_HASH, str):
        return LOGGER.error("Invalid API_ID or API_HASH. Please check your credentials.")

    LOGGER.error(f"Cloning bot for user {user_id}...")
    directory_path = f"/app/Emilia-{user_id}"
    git_repo_url = "https://github.com/tusarhushena/Emilia.git"

    if os.path.exists(directory_path):
        os.chdir(directory_path)
        subprocess.run(["git", "reset", "--hard"])  # Discard uncommitted changes
        subprocess.run(["git", "pull", "--rebase"])
    else:
        subprocess.run(["git", "clone", "--depth=1", git_repo_url, directory_path])
    LOGGER.error(f"Repository cloned for user {user_id}")

    bot_id, bot_username, bot_name = await get_bot_info(token, user_id)
    if not bot_id:
        return LOGGER.error("Failed to retrieve bot information. Aborting clone.")

    # Write the config file
    file_path = f"{directory_path}/Emilia/config.py"
    with open(file_path, "w") as file:
        file.write(CONFIG_TEMPLATE.format(
            api_id=API_ID, api_hash=API_HASH, bot_id=bot_id,
            bot_username=bot_username, bot_token=token, bot_name=bot_name
        ))

    LOGGER.error("Config written. Starting cloned bot...")
    os.chdir(directory_path)
    asyncio.create_task(run_and_restart_cloned_bot(directory_path))

async def delete_clone(user_id):
    """
    Deletes a cloned bot and stops it.
    """
    await clone_db.delete_many({"_id": user_id})
    folder_path = f"/app/Emilia-{user_id}"
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    await timer.insert_one({"_id": user_id, "time": datetime.now()})
    LOGGER.error(f"Deleted cloned bot for user {user_id}.")

@register(pattern="clone")
async def clone_bot(event):
    """
    Users can clone the bot by providing their bot token via /clone <bottoken>.
    """
    if not ORIGINAL_EVENT_LOOP:
        return await event.reply("This feature is only available for the original bot.")
    if not event.is_private:
        return await event.reply("Please use the /clone command in your private chat.")
    user_id = event.sender_id
    if await clone_db.find_one({"_id": user_id}):
        return await event.reply("You have already cloned the bot. Use /deleteclone <bottoken> to delete it.")
    bots = await clone_db.count_documents({})
    if bots >= CLONE_LIMIT:
        return await event.reply(f"Clone limit reached ({CLONE_LIMIT}). Please contact @{SUPPORT_CHAT} for more clones.")
    if len(event.text.split()) < 2:
        return await event.reply("Please provide your bot token from @BotFather. Example: `/clone 219218219:jksswq`")
    token = event.text.split(None, 1)[1]
    if await clone_db.find_one({"token": token}):
        return await event.reply("This bot token has already been used. Please use a different token.")

    wait = await event.reply("Cloning the bot. Please wait...")
    bot_id, bot_username, bot_name = await get_bot_info(token, user_id)
    if not bot_id:
        return await event.reply("Invalid bot token. Please check and try again.")

    await clone_db.insert_one({"_id": user_id, "token": token})
    await event.reply("Cloned successfully. Your bot will start shortly.\nUse `/deleteclone <bottoken>` to delete your clone.")
    
    try:
        await clone(user_id, token)
    except Exception as e:
        LOGGER.error(f"Error during cloning: {e}")
        await clone_db.delete_many({"_id": user_id})
        await event.reply("An error occurred while cloning the bot. Please try again or contact support.")
    await wait.delete()
   
async def delete_folder(folder_path):
    if os.path.exists(folder_path):
        for path, subdirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                os.remove(os.path.join(path, name))
            for name in subdirs:
                shutil.rmtree(os.path.join(path, name))
        os.rmdir(folder_path)

@register(pattern="deleteclone")
async def delete_cloned(event):
    """
    Users can delete their cloned bot using /deleteclone <bottoken>.
    The token is verified, the clone entry is removed from the DB,
    and the cloned bot’s folder is deleted.
    """
    if not ORIGINAL_EVENT_LOOP:
        return await event.reply("This feature is only available for the original bot.")
    if not event.is_private:
        return await event.reply("Please use your private chat to delete your clone.")
    user_id = event.sender_id
    clone_info = await clone_db.find_one({"_id": user_id})
    if not clone_info:
        return await event.reply("You haven't cloned the bot yet. Use `/clone <bottoken>` to clone it.")
    if len(event.text.split()) < 2:
        return await event.reply("Please provide the bot token to delete the clone. Example: `/deleteclone 219218219:jksswq`")
    token = event.text.split(None, 1)[1]
    if clone_info["token"] != token:
        return await event.reply("The provided bot token is incorrect.")
    await clone_db.delete_many({"_id": user_id})
    await delete_folder(f"/app/Emilia-{user_id}")
    await timer.insert_one({"_id": user_id, "time": datetime.now()})
    await event.reply("Your cloned bot has been deleted. It will be stopped within 12 hours.")

async def delete_clone(user_id):
    await clone_db.delete_many({"_id": user_id})
    await delete_folder(f"/app/Emilia-{user_id}")
    try:
        await timer.insert_one({"_id": user_id, "time": datetime.now()})
    except DuplicateKeyError:
        LOGGER.error(f"Duplicate timer entry for user {user_id}.")
    LOGGER.error(f"Deleted cloned bot for user {user_id}.")

@register(pattern="broadcast")
async def broadcast(event):
    """
    Dev users (or the main clone owner) can broadcast a message by replying to a message 
    and using one of the flags: -all, -users, or -chats.
    """
    # Allow if sender is a developer; otherwise check if they are the clone owner (token matches main bot)
    if event.sender_id not in DEV_USERS:
        clone_info = await clone_db.find_one({"_id": event.sender_id})
        if not clone_info:
            return await event.reply("You haven't cloned the bot yet. Use `/clone <bottoken>` to clone it.")
        if clone_info["token"] != TOKEN:
            return await event.reply("Only the owner of the cloned bot can broadcast messages.")
    
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("Please reply to a message to broadcast.")
    text = event.text.split(None, 1)
    if len(text) < 2:
        return await event.reply("Please provide a flag: `/broadcast -all`, `/broadcast -users`, or `/broadcast -chats`")
    flag = text[1].strip()
    if flag == "-all":
        await user_broadcast(event, reply)
        await chat_broadcast(event, reply)
    elif flag == "-users":
        await user_broadcast(event, reply)
    elif flag == "-chats":
        await chat_broadcast(event, reply)
    else:
        await event.reply("Invalid flag. Use `/broadcast -all`, `/broadcast -users`, or `/broadcast -chats`")

async def user_broadcast(event, reply):
    async for user in user_db.find({}):
        try:
            await telethn.forward_messages(user["user_id"], reply)
        except errors.FloodWaitError as e:
            await sleep(e.seconds)
            continue
        except Exception:
            pass
    await event.reply("Broadcasted message to all users successfully.")

async def chat_broadcast(event, reply):
    async for chat in chat_db.find({}):
        try:
            await telethn.forward_messages(chat["chat_id"], reply)
        except errors.FloodWaitError as e:
            await sleep(e.seconds)
            continue
        except Exception:
            pass
    await event.reply("Broadcasted message to all chats successfully.")
