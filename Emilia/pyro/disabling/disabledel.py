from pyrogram import Client, enums

import Emilia.strings as strings
from Emilia import custom_filter
from Emilia.helper.chat_status import check_bot, check_user
from Emilia.mongo.disable_mongo import disabledel_db
from Emilia.pyro.connection.connection import connection
from Emilia.utils.decorators import *

DISABLEDEL_TRUE = ["on", "yes"]
DISABLEDEL_FALSE = ["off", "no"]


@usage("/disabledel [on/off | yes/no]")
@example("/disabledel on")
@description(
    "By turning it on, bot will automatically delete the commands that are disabled in a chat for non-admins."
)
@Client.on_message(custom_filter.command(commands="disabledel"))
async def disabledel(client, message):
    if await connection(message) is not None:
        chat_id = await connection(message)
    else:
        chat_id = message.chat.id

    if (
        not str(chat_id).startswith("-100")
        and message.chat.type == enums.ChatType.PRIVATE
    ):
        return await message.reply(strings.is_pvt)

    if not await check_bot(message, privileges="can_delete_messages"):
        return

    if not await check_user(message, privileges="can_change_info"):
        return

    if len(message.text.split()) >= 2:
        arg = message.text.split()[1]
        if arg in DISABLEDEL_TRUE:
            await disabledel_db(chat_id, True)
            await message.reply("Disabled messages will now be deleted.")

        elif arg in DISABLEDEL_FALSE:
            await disabledel_db(chat_id, False)
            await message.reply("Disabled messages will no longer be deleted.")

        else:
            await message.reply(
                "Your input was not recognised as one of: yes/no/on/off"
            )
    else:
        await usage_string(message, disabledel)
        return
