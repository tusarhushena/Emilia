from pyrogram import Client

from Emilia import custom_filter
from Emilia.helper.disable import disable
from Emilia.pyro.locks import lock_map


@Client.on_message(custom_filter.command(commands="locktypes", disable=True))
@disable
async def locktypes(client, message):
    LOCKS_LIST = lock_map.LocksMap.list()

    text = "The available locktypes are:\n"
    for lock in LOCKS_LIST:
        text += f"• {lock}\n"

    await message.reply(text, quote=True)
