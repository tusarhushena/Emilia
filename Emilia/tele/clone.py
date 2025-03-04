import os
import subprocess
import asyncio
import shutil

from datetime import datetime, timedelta
from pymongo.errors import DuplicateKeyError
from telethon import TelegramClient, errors

from Emilia import API_HASH, API_ID, LOGGER, db, DEV_USERS, TOKEN, telethn, CLONE_LIMIT, SUPPORT_CHAT
from Emilia.custom_filter import register
from Emilia.tele.backup import send
from Emilia import config

# Database collections
clone_db = db.clone
timer = db.timer
user_db = db.users
chat_db = db.chats

@register(pattern="stats")
async def stats_(event):
    if event.sender_id not in DEV_USERS:
        return await event.reply("Only my Developer can use this command!")
    users = await user_db.count_documents({})
    chats = await chat_db.count_documents({})
    bots = await clone_db.count_documents({})
    message = f"**Chats**: {chats}\n**Users**: {users}\n**Cloned Bots Active**: {bots}"
    await event.reply(message)

async def run_and_restart_cloned_bot(directory_path):
    """ Continuously runs and restarts the cloned bot every 24 hours. """
    while True:
        LOGGER.info(f"Starting cloned bot from: {directory_path}")
        process = await asyncio.create_subprocess_exec(
            "python3", "-m", "Emilia",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=directory_path
        )
        try:
            await asyncio.wait_for(process.wait(), timeout=86400)  # Run for 24 hours
        except asyncio.TimeoutError:
            LOGGER.info("24 hours passed, restarting cloned bot...")
            process.kill()
            await process.wait()
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            LOGGER.error(f"Cloned bot error: {stderr.decode()}")
        await asyncio.sleep(5)

async def get_bot_info(token):
    try:
        client = TelegramClient("clone-test", API_ID, API_HASH)
        await client.start(bot_token=token)
        bot = await client.get_me()
        await client.disconnect()
        return bot.id, bot.username, bot.first_name
    except errors.AccessTokenExpiredError:
        return "expired", None, None
    except Exception as e:
        LOGGER.error(f"Error getting bot info: {e}")
        return None, None, None

async def clone(user_id, token):
    """ Clones a new bot and starts it immediately. """
    existing_clone = await clone_db.find_one({"_id": user_id})
    if existing_clone:
        return

    LOGGER.info(f"Cloning bot for user {user_id}...")
    directory_path = f"/root/Emilia-{user_id}"
    git_repo_url = "https://github.com/tusarhushena/Emilia.git"

    # Clone repository
    if os.path.exists(directory_path):
        os.chdir(directory_path)
        subprocess.run(["git", "pull", "--rebase"])
    else:
        subprocess.run(["git", "clone", "--depth=1", git_repo_url, directory_path])

    bot_id, bot_username, bot_name = await get_bot_info(token)
    if not bot_id:
        return

    # Write bot config
    config_path = f"{directory_path}/Emilia/config.py"
    with open(config_path, "w") as file:
        file.write(f"""
API_HASH = "{API_HASH}"
API_ID = {API_ID}
BOT_ID = {bot_id}
BOT_USERNAME = "{bot_username}"
TOKEN = "{token}"
""")

    LOGGER.info("Config written. Starting cloned bot...")
    os.chdir(directory_path)

    # Save to database
    await clone_db.insert_one({"_id": user_id, "token": token})

    # Start the bot and ensure it runs continuously
    asyncio.create_task(run_and_restart_cloned_bot(directory_path))

async def clone_start_up():
    """ Starts all cloned bots on main bot startup. """
    all_users = await clone_db.find({}).to_list(length=None)
    tasks = []
    for user in all_users:
        user_id = user["_id"]
        token = user["token"]
        tasks.append(asyncio.create_task(clone(user_id, token)))
    await asyncio.gather(*tasks)

@register(pattern="clone")
async def clone_bot(event):
    """ Allows users to clone the bot using /clone <bottoken>. """
    if not event.is_private:
        return await event.reply("Use this command in private chat.")
    
    user_id = event.sender_id
    if await clone_db.find_one({"_id": user_id}):
        return await event.reply("You already have a cloned bot. Use /deleteclone to remove it.")

    if len(event.text.split()) < 2:
        return await event.reply("Please provide your bot token: `/clone <bottoken>`")

    token = event.text.split(None, 1)[1]

    # Prevent duplicate bot tokens
    if await clone_db.find_one({"token": token}):
        return await event.reply("This token has already been used.")

    wait = await event.reply("Cloning the bot...")

    try:
        bot_id, bot_username, bot_name = await get_bot_info(token)
        if bot_id == "expired":
            await wait.delete()
            return await event.reply("Invalid bot token. Please check and try again.")
    except Exception as e:
        LOGGER.error(f"Error testing token: {e}")
        await wait.delete()
        return await event.reply("Error verifying token. Try again later.")

    # Start the clone process
    await clone(user_id, token)
    await wait.delete()
    await event.reply("Bot cloned successfully! It will start shortly.")

@register(pattern="deleteclone")
async def delete_cloned(event):
    """ Allows users to delete their cloned bot using /deleteclone. """
    if not event.is_private:
        return await event.reply("Use this command in private chat.")

    user_id = event.sender_id
    clone_info = await clone_db.find_one({"_id": user_id})
    if not clone_info:
        return await event.reply("You don't have a cloned bot.")

    # Delete from DB and remove files
    await clone_db.delete_one({"_id": user_id})
    await delete_folder(f"/root/Emilia-{user_id}")

    await event.reply("Your cloned bot has been deleted.")

async def delete_folder(folder_path):
    """ Deletes the specified folder and its contents. """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

@register(pattern="broadcast")
async def broadcast(event):
    """ Allows the bot owner to broadcast messages. """
    if event.sender_id not in DEV_USERS:
        return await event.reply("Only bot developers can use this.")

    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("Reply to a message to broadcast.")

    flag = event.text.split()[-1]
    if flag not in ["-all", "-users", "-chats"]:
        return await event.reply("Use: `/broadcast -all`, `/broadcast -users`, or `/broadcast -chats`")

    if flag in ["-all", "-users"]:
        await user_broadcast(event, reply)
    if flag in ["-all", "-chats"]:
        await chat_broadcast(event, reply)

async def user_broadcast(event, reply):
    async for user in user_db.find({}):
        try:
            await telethn.forward_messages(user["user_id"], reply)
        except:
            pass
    await event.reply("Broadcasted to all users.")

async def chat_broadcast(event, reply):
    async for chat in chat_db.find({}):
        try:
            await telethn.forward_messages(chat["chat_id"], reply)
        except:
            pass
    await event.reply("Broadcasted to all chats.")
