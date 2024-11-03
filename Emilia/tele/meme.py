# DONE: Memes

import random

from requests import get

from Emilia.custom_filter import register
from Emilia.helper.disable import disable
from Emilia.utils.decorators import exception

MemesReddit = [
    "Animemes",
    "lostpause",
    "LoliMemes",
    "cleananimemes",
    "animememes",
    "goodanimemes",
    "AnimeFunny",
    "dankmemes",
    "teenagers",
    "shitposting",
    "Hornyjail",
    "wholesomememes",
    "cursedcomments",
]


@register(pattern="memes", disable=True)
@disable
@exception
async def mimi(event):
    memereddit = random.choice(MemesReddit)
    meme_link = f"https://meme-api.com/gimme/{memereddit}"
    q = get(meme_link).json()
    await event.reply(q["title"], file=q["url"])


@register(pattern="dank", disable=True)
@disable
@exception
async def mimi(event):
    meme_link = "https://meme-api.com/gimme/dankmemes"
    q = get(meme_link).json()
    await event.reply(q["title"], file=q["url"])


@register(pattern="lolimeme", disable=True)
@disable
@exception
async def mimi(event):
    meme_link = "https://meme-api.com/gimme/LoliMemes"
    q = get(meme_link).json()
    await event.reply(q["title"], file=q["url"])


@register(pattern="hornyjail", disable=True)
@disable
@exception
async def mimi(event):
    meme_link = "https://meme-api.com/gimme/Hornyjail"
    q = get(meme_link).json()
    await event.reply(q["title"], file=q["url"])


@register(pattern="wmeme", disable=True)
@disable
@exception
async def mimi(event):
    meme_link = "https://meme-api.com/gimme/wholesomememes"
    q = get(meme_link).json()
    await event.reply(q["title"], file=q["url"])


@register(pattern="pewds", disable=True)
@disable
@exception
async def mimi(event):
    meme_link = "https://meme-api.com/gimme/PewdiepieSubmissions"
    q = get(meme_link).json()
    await event.reply(q["title"], file=q["url"])


@register(pattern="hmeme", disable=True)
@disable
@exception
async def mimi(event):
    meme_link = "https://meme-api.com/gimme/hornyresistance"
    q = get(meme_link).json()
    await event.reply(q["title"], file=q["url"])


@register(pattern="teen", disable=True)
@disable
@exception
async def mimi(event):
    meme_link = "https://meme-api.com/gimme/teenagers"
    q = get(meme_link).json()
    await event.reply(q["title"], file=q["url"])


@register(pattern="fbi", disable=True)
@disable
@exception
async def mimi(event):
    meme_link = "https://meme-api.com/gimme/FBI_Memes"
    q = get(meme_link).json()
    await event.reply(q["title"], file=q["url"])


@register(pattern="shitposting", disable=True)
@disable
@exception
async def mimi(event):
    meme_link = "https://meme-api.com/gimme/shitposting"
    q = get(meme_link).json()
    await event.reply(q["title"], file=q["url"])


@register(pattern="cursed", disable=True)
@disable
@exception
async def mimi(event):
    meme_link = "https://meme-api.com/gimme/cursedcomments"
    q = get(meme_link).json()
    await event.reply(q["title"], file=q["url"])
