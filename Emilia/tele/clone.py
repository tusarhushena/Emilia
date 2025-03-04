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

startpic = "https://files.catbox.moe/ka9qcw.jpg"

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
    await asyncio.sleep(5)
    LOGGER.info(f"Waiting for 5 seconds before creating bot for user {user_id}")
    directory_path = f"/root/Emilia-{user_id}"

    LOGGER.info(f"Cloning the repository for user {user_id}")
    git_repo_url = "https://github.com/tusarhushena/Emilia.git"
    try:
        subprocess.run(["git", "clone", git_repo_url, directory_path], check=True)
    except Exception as e:
        LOGGER.error(f"An error occurred while cloning the repository: {e}")
        LOGGER.info("Pulling the repository instead")
        os.chdir(directory_path)
        subprocess.run(["git", "pull"], check=True)

    LOGGER.info(f"Repository cloned for user {user_id}")
    file_path = f"{directory_path}/Emilia/config.py"

    bot_id, bot_username, bot_name = await get_bot_info(token)
    if not (bot_id and bot_username and bot_name):
        LOGGER.error("Failed to retrieve bot details. Using default values.")
        bot_id = 7741293072
        bot_username = "HarrClonerBot"
        bot_name = "Harry"
    if bot_id == "expired":
        return

    # Fetch start picture URL
    mm = await startpic.find_one({"token": TOKEN})
    start_pic_url = mm["url"] if mm else "https://files.catbox.moe/ka9qcw.jpg"

    # Format config file correctly
    config_content = config_template.format(
        api_hash=API_HASH,
        api_id=API_ID,
        bot_id=bot_id,
        bot_username=bot_username,
        mongo_url=db.connection_string,
        support_chat=SUPPORT_CHAT,
        update_channel="",
        start_pic=start_pic_url,
        dev_users=DEV_USERS,
        token=token,
        owner_id=user_id,
        clone_limit=CLONE_LIMIT,
        bot_name=bot_name
    )

    # Write the config file
    try:
        with open(file_path, "w") as file:
            file.write(config_content)
    except Exception as e:
        LOGGER.error(f"Failed to write config.py: {e}")
        return

    LOGGER.info("Config.py written successfully")

    # Run the cloned bot
    os.chdir(directory_path)
    await run_and_restart_cloned_bot(directory_path)

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
