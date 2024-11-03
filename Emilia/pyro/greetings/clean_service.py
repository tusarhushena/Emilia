from pyrogram import Client

from Emilia import custom_filter
from Emilia.helper.chat_status import CheckAllAdminsStuffs
from Emilia.mongo.welcome_mongo import GetCleanService, SetCleanService
from Emilia.pyro.connection.connection import connection
from Emilia.utils.decorators import *

CLEAN_SERVICE_TRUE = ["on", "yes"]
CLEAN_SERVICE_FALSE = ["off", "no"]


@Client.on_message(custom_filter.command(commands="cleanservice"))
@anonadmin_checker
async def CleanService(client, message):
    if await connection(message) is not None:
        chat_id = await connection(message)
    else:
        chat_id = message.chat.id

    if not (await CheckAllAdminsStuffs(message, privileges="can_delete_messages")):
        return

    command = message.text.split(" ")
    if not (len(command) == 1):
        get_clean_service = command[1]

        if get_clean_service in CLEAN_SERVICE_TRUE:
            clean_service = True
            await SetCleanService(chat_id, clean_service)
            await message.reply(
                "I'll be deleting all service messages from now on!", quote=True
            )

        elif get_clean_service in CLEAN_SERVICE_FALSE:
            clean_service = False
            await SetCleanService(chat_id, clean_service)
            await message.reply("I'll leave service messages.", quote=True)

        else:
            await message.reply(
                "Your input was not recognised as one of: yes/no/on/off", quote=True
            )

    elif len(command) == 1:
        if await GetCleanService(chat_id):
            CleanServiceis = "I am currently deleting service messages when new members join or leave."

        else:
            CleanServiceis = "I am not currently deleting service messages when members join or leave."

        await message.reply(
            (
                f"{CleanServiceis}\n\n"
                "To change this setting, try this command again followed by one of yes/no/on/off"
            ),
            quote=True,
        )
