# DONE: Stickers

import random
from asyncio import sleep

import emoji
from bs4 import BeautifulSoup
from requests import get
from telethon import Button
from telethon.errors import FloodWaitError
from telethon.errors.rpcerrorlist import PackShortNameOccupiedError
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.functions.stickers import CreateStickerSetRequest
from telethon.tl.types import (
    DocumentAttributeSticker,
    InputDocument,
    InputStickerSetEmpty,
    InputStickerSetID,
    InputStickerSetItem,
)

from Emilia import db, telethn
from Emilia.custom_filter import register
from Emilia.helper.disable import disable
from Emilia.utils.decorators import *

pkang = db.pkang


def get_emoji(v):
    p = "".join(c for c in v if c in emoji.UNICODE_EMOJI["en"])
    if len(p) != 0:
        return p[0]
    return None


@register(pattern="pkang|packkang", disable=True)
@disable
async def pck_kang__(e):
    if not e.reply_to:
        return await e.reply("Please reply to a sticker.")
    r = await e.get_reply_message()
    if not r.sticker:
        return await e.reply("That's not a sticker file. Please reply to a sticker.")
    if len(e.text.split(" ", 1)) == 2:
        pname = e.text.split(" ", 1)[1]
        emoji_ = get_emoji(pname)
        if emoji_:
            if pname.startswith(emoji_):
                emoji_ = None
            else:
                pname = pname.replace(emoji_, "")
    else:
        pname = f"{e.sender.first_name}'s pKang pack"
        emoji_ = None
    id = access_hash = None
    for x in r.sticker.attributes:
        if isinstance(x, DocumentAttributeSticker):
            if not isinstance(x.stickerset, InputStickerSetEmpty):
                id = x.stickerset.id
                access_hash = x.stickerset.access_hash
    if not (id or access_hash):
        return await e.reply("That sticker is not part of any pack to kang!")

    _stickers = await telethn(
        GetStickerSetRequest(
            stickerset=InputStickerSetID(id=id, access_hash=access_hash), hash=0
        )
    )
    stk = []
    if emoji_:
        for x in _stickers.documents:
            stk.append(
                InputStickerSetItem(
                    document=InputDocument(
                        id=x.id,
                        access_hash=x.access_hash,
                        file_reference=x.file_reference,
                    ),
                    emoji=emoji_,
                )
            )
    else:
        for x in _stickers.documents:
            stk.append(
                InputStickerSetItem(
                    document=InputDocument(
                        id=x.id,
                        access_hash=x.access_hash,
                        file_reference=x.file_reference,
                    ),
                    emoji=(x.attributes[1]).alt,
                )
            )
    pack = 1
    xp = await pkang.find_one({"user_id": e.sender_id})
    if xp:
        pack = xp.get("pack") + 1
    await pkang.update_one(
        {"user_id": e.sender_id}, {"$set": {"pack": pack}}, upsert=True
    )
    pm = random.choice(
        ["af", "bq", "cj", "dp", "eu", "fw", "g", "hu", "wuw", "uw", "hk", "lm", "jr"]
    )
    try:
        p = await telethn(
            CreateStickerSetRequest(
                user_id=e.sender_id,
                title=pname,
                short_name=f"{pm}{e.sender_id}_{pack}_by_Elf_Robot",
                stickers=stk,
            )
        )
    except PackShortNameOccupiedError:
        await sleep(5)
        pack += 1
        p = await telethn(
            CreateStickerSetRequest(
                user_id=e.sender_id,
                title=pname + f"Vol {pack}",
                short_name=f"{pm}{e.sender_id}_{pack}_by_Elf_Robot",
                stickers=stk,
            )
        )
    except FloodWaitError as e:
        await sleep(e.seconds)
    except Exception as ex:
        return await e.reply(str(ex))
    await e.reply(
        f"Sticker set successfully created and added to <b><a href='http://t.me/addstickers/{p.set.short_name}'>Pack</a></b>.",
        buttons=Button.url(
            "View Pack", url=f"http://t.me/addstickers/{p.set.short_name}"
        ),
        parse_mode="html",
    )


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.63 Safari/537.36"
}


@usage("/stickers [query]")
@description("Searches for stickers in combot.org")
@example("/stickers pepe")
@register(pattern="stickers", disable=True)
@disable
async def search_combot_stickers__(e):
    if len(e.text.split(" ", 1)) == 2:
        q = e.text.split(" ", 1)[1]
    else:
        return await usage_string(e, search_combot_stickers__)
    url = "https://combot.org/telegram/stickers?q={}".format(q)
    r = get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    results = soup.find_all("a", {"class": "sticker-pack__btn"})
    if not results:
        return await e.reply("No results found :(")
    titles = soup.find_all("div", "sticker-pack__title")
    text = "Stickers for **{}**".format(q)
    Q = 1
    for x, y in zip(results, titles):
        if Q == 7:
            break
        Q += 1
        text += "\n• [{}]({})".format(y.get_text(), x["href"])
    await e.reply(text)
