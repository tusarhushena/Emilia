import re

from pyrogram import Client, filters
from urlextract import URLExtract

from Emilia import db
from Emilia.helper.chat_status import isBotAdmin, isUserAdmin
from Emilia.mongo.blocklists_mongo import get_blocklist
from Emilia.pyro.blocklists.checker import blocklist_action

collection = db["approve_d"]


@Client.on_message(filters.all & filters.group, group=3)
async def blocklist_checker(client, message):
    if not (message.from_user or message.sender_chat):
        return
    chat_id = message.chat.id

    try:
        if not await isBotAdmin(message, silent=True):
            return
        if await isUserAdmin(message, silent=True):
            return
    except BaseException:
        pass

    if message.sender_chat:
        user_id = message.sender_chat.id

    else:
        user_id = message.from_user.id

    if await collection.find_one({"user_id": user_id, "chat_id": chat_id}):
        return

    BLOCKLIST_DATA = await get_blocklist(chat_id)
    if BLOCKLIST_DATA is None or len(BLOCKLIST_DATA) == 0:
        return

    BLOCKLIST_ITMES = []
    for blocklist_array in BLOCKLIST_DATA:
        BLOCKLIST_ITMES.append(blocklist_array["blocklist_text"])

    message_text = extract_text(message)

    for blitmes in BLOCKLIST_ITMES:
        if "*" in blitmes:
            star_position = blitmes.index("*")
            if blitmes[star_position - 1] == "/":
                block_char = blitmes[:star_position]
                extractor = URLExtract()
                URLS = extractor.find_urls(message_text)
                for url in URLS:
                    if block_char in url:
                        await blocklist_action(client, message, f"{block_char}*")
                        return

            elif len(blitmes) > len(blitmes) and blitmes[star_position + 1] == ".":
                if message.document or message.animation:
                    extensions = blitmes[star_position + 1 :]
                    file_name = None
                    if message.document:
                        file_name = message.document.file_name
                    elif message.animation:
                        file_name = message.animation.file_name
                    if file_name.endswith(extensions):
                        await blocklist_action(client, message, f"*{extensions}")
                        return
        else:
            if message_text is not None:
                pattern = r"( |^|[^\w])" + re.escape(blitmes) + r"( |$|[^\w])"
                if re.search(pattern, message_text, flags=re.IGNORECASE):
                    await blocklist_action(client, message, blitmes)
                    return


def extract_text(message) -> str:
    return (
        message.text
        or message.caption
        or (message.sticker.emoji if message.sticker else None)
    )
