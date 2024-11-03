# DONE: Google

from urllib.parse import quote

from requests import get
from telethon import *
from telethon.tl.types import *

from Emilia.custom_filter import register
from Emilia.helper.disable import disable
from Emilia.utils.decorators import *


@usage("/google [query]")
@example("/google shinobinet on telegram")
@description("This will send multiple links from Google or Bing.")
@register(pattern="google|bing", disable=True)
@disable
@exception
async def google(event):
    query = event.text.split(None, 1)[1]

    if not query:
        return await usage_string(event, google)

    q = quote(query)
    wait = await event.reply("Searching on the internet. Please wait :3")

    google_url = f"https://www.google.com/search?q={q}"
    google_button = Button.url("Google", google_url)

    search_results = []

    bing_search_url = f"https://api.akuari.my.id/search/bingsearch?query={q}"
    bing_results = get(bing_search_url).json()

    for result in bing_results.get("hasil", {}).get("results", [])[:20]:
        title = result.get("title", "")
        description = result.get("description", "")
        url = result.get("url", "")

        if description:
            search_results.append(f"• [{title}]({url})\n__{description}__")

    meow = (
        f"**Search results of {query.replace('%20', ' ')} on the internet:**\n\n"
        + "\n\n".join(search_results)
    )

    try:
        await event.reply(meow, buttons=[google_button], link_preview=False)
    except errors.ChatWriteForbiddenError:
        await event.reply(meow, link_preview=False)
    await wait.delete()
