# DONE: Misc

import os
import random

from gtts import gTTS
from mutagen.mp3 import MP3
from requests import get
from telethon.tl.types import DocumentAttributeAudio

from Emilia import telethn as meow, BOT_NAME
from Emilia.custom_filter import register
from Emilia.helper.disable import disable
from Emilia.utils.decorators import *


@register(pattern="(count|gstat)")
async def ___stat_chat__(e):
    __stats_format = "**Total Messages in {}:** `{}`"
    await e.reply(__stats_format.format(e.chat.title, e.id))


@usage("/tts [LanguageCode] <text>")
@example("/tts en Hello")
@description("This will convert the given text to speech.")
@register(pattern="tts", disable=True)
@disable
@exception
async def tts(event):
    if not event.reply_to_msg_id and event.text.split(None, 1)[1]:
        text = event.text.split(None, 1)[1]
        _total = text.split(None, 1)
        if len(_total) == 2:
            lang = (_total[0]).lower()
            text = _total[1]
        else:
            lang = "en"
            text = _total[0]
    elif event.reply_to_msg_id:
        text = (await event.get_reply_message()).text
        if event.pattern_match.group(1):
            lang = (event.text.split(None, 1)[1]).lower()
        else:
            lang = "en"
    else:
        return await usage_string(event, tts)
    try:
        tts = gTTS(text, tld="com", lang=lang)
        tts.save("stt.mp3")
    except BaseException as e:
        return await event.reply(str(e))
    aud_len = int((MP3("stt.mp3")).info.length)
    if aud_len == 0:
        aud_len = 1
    async with meow.action(event.chat_id, "record-voice"):
        await event.respond(
            file="stt.mp3",
            attributes=[
                DocumentAttributeAudio(
                    duration=aud_len,
                    title=f"stt_{lang}",
                    performer=f"{BOT_NAME}",
                    waveform="320",
                )
            ],
        )
        os.remove("stt.mp3")


# DONE: GIFs
@usage("/gif [query]")
@example("/gif cats ; 5")
@description(
    "This will send desired GIF, if you need multiple GIFs look at the example."
)
@register(pattern="gif", disable=True)
@disable
@exception
async def some(event):
    inpt = event.text.split(None, 1)[1]
    if not inpt:
        return await usage_string(event, some)
    count = 1
    if ";" in inpt:
        inpt, count = inpt.split(";")
    if int(count) < 0 and int(count) > 20:
        return await event.reply("Give number of GIFs between 1-20.")
    res = get("https://giphy.com/")
    res = res.text.split("GIPHY_FE_WEB_API_KEY =")[1].split("\n")[0]
    api_key = res[2:-1]
    r = get(
        f"https://api.giphy.com/v1/gifs/search?q={inpt}&api_key={api_key}&limit=50"
    ).json()
    list_id = [r["data"][i]["id"] for i in range(len(r["data"]))]
    rlist = random.sample(list_id, int(count))
    for items in rlist:
        await event.client.send_file(
            event.chat_id,
            f"https://media.giphy.com/media/{items}/giphy.gif",
            reply_to=event,
        )
