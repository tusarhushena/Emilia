import os
import re

import aiofiles
import httpx
from pyrogram import Client

from Emilia import custom_filter
from Emilia.helper.disable import disable
from Emilia.utils.decorators import *

pattern = re.compile(r"^text/|json$|yaml$|xml$|toml$|x-sh$|x-shellscript$")


http = httpx.AsyncClient()


@usage("/paste [reply to text/file]")
@example("/paste ArshCypherZ is a good boi")
@description("This command will paste the given text or replied file to nekobin.com")
@Client.on_message(custom_filter.command(commands="paste", disable=True))
@disable
async def paste_func(_, message):
    if not message.reply_to_message:
        await usage_string(message, paste_func)
        return
    if message.reply_to_message.text:
        content = str(message.reply_to_message.text)
    elif message.reply_to_message.document:
        document = message.reply_to_message.document
        if document.file_size > 1048576:
            return await message.reply("You can only paste files smaller than 1MB.")
        if not pattern.search(document.mime_type):
            return await message.reply("Only text files can be pasted.")
        doc = await message.reply_to_message.download()
        async with aiofiles.open(doc, mode="r") as f:
            content = await f.read()
        os.remove(doc)

    link = "https://nekobin.com/api/documents"
    r = await http.post(link, json={"content": content})
    url = f"https://nekobin.com/{r.json()['result']['key']}"
    return await message.reply(url, disable_web_page_preview=True)
