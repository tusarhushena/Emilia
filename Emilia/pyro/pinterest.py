import asyncio
import random

from pyrogram import Client
from requests import get

from Emilia import custom_filter
from Emilia.helper.disable import disable
from Emilia.utils.decorators import *


@usage("/pinterest [query]")
@example("/pinterest anime icon hd")
@description("This will fetch images from pinterest app.")
@Client.on_message(custom_filter.command(commands="pinterest", disable=True))
@disable
async def pin(client, message):
    msgs = message.text.split(" ", 1)
    if len(msgs) == 1:
        await usage_string(message, pin)
        return
    msg = msgs[1]
    try:
        img = get(f"https://pinterest-api-one.vercel.app/?q={msg}").json()
        count = img["count"]
        list_id = [img["images"][i] for i in range(count)]
        item = (random.sample(list_id, 1))[0]

        await message.reply_photo(photo=item)
        await asyncio.sleep(2)
    except Exception:
        await message.reply_text("No results found. Try something else!")
