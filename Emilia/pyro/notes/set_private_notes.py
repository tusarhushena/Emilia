from pyrogram import Client

from Emilia import custom_filter
from Emilia import BOT_NAME
from Emilia.helper.chat_status import isUserAdmin
from Emilia.mongo.notes_mongo import is_pnote_on, set_private_note
from Emilia.pyro.connection.connection import connection

PRIVATE_NOTES_TRUE = ["on", "true", "yes", "y"]
PRIVATE_NOTES_FALSE = ["off", "false", "no", "n"]


@Client.on_message(custom_filter.command(commands="privatenotes"))
async def PrivateNote(client, message):
    if await connection(message) is not None:
        chat_id = await connection(message)
    else:
        chat_id = message.chat.id

    if not await isUserAdmin(message, chat_id=chat_id, pm_mode=True):
        return

    command = message.text.split(" ")
    if not (len(command) == 1):
        if command[1] in PRIVATE_NOTES_TRUE:
            await message.reply(
                f"{BOT_NAME} will now send a message to your chat with a button redirecting to PM, where the user will receive the note.",
                quote=True,
            )
            await set_private_note(chat_id, True)

        elif command[1] in PRIVATE_NOTES_FALSE:
            await message.reply(
                f"{BOT_NAME} will now send notes straight to the group.", quote=True
            )
            await set_private_note(chat_id, False)

        else:
            await message.reply(
                f"failed to get boolean value from input: expected one of y/yes/on/true or n/no/off/false; got: {message.text.split()[1]}",
                quote=True,
            )
    else:
        if await is_pnote_on(chat_id):
            await message.reply(
                f"Your notes are currently being sent in private. {BOT_NAME} will send a small note with a button which redirects to a private chat.",
                quote=True,
            )
        else:
            await message.reply(
                "Your notes are currently being sent in the group.", quote=True
            )
