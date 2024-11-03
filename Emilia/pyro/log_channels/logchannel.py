import html

from pyrogram import Client

from Emilia import custom_filter
from Emilia.helper.chat_status import isUserAdmin
from Emilia.mongo.log_channels_mongo import get_set_channel
from Emilia.pyro.connection.connection import connection
from Emilia.utils.decorators import *


@Client.on_message(custom_filter.command(commands=("logchannel")))
@anonadmin_checker
async def logcategories(client, message):

    if await connection(message) is not None:
        chat_id = await connection(message)
    else:
        chat_id = message.chat.id

    if not await isUserAdmin(message, pm_mode=True):
        return

    if await get_set_channel(chat_id) is not None:
        channel_title = await get_set_channel(chat_id)
        await message.reply(
            f"I am currently logging admin actions in '{html.escape(channel_title)}'.",
            quote=True,
        )
    else:
        await message.reply(
            "There are no log channels assigned to this chat.", quote=True
        )
