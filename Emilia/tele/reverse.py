import traceback
from telethon.tl.types import MessageMediaPhoto
from Emilia.custom_filter import register
from Emilia.helper.disable import disable
from Emilia.utils.decorators import *
from Emilia.tele.grs import GoogleLens
from Emilia.catbox import upload

lens = GoogleLens()

@usage("/reverse [reply to image]")
@description("Will reverse search the image you replied to.")
@example("/reverse (reply to image)")
@register(pattern="grs|reverse|pp", disable=True)
@disable
async def reverse(event):
    async def process_and_reply(reply_message, url):
        try:
            result = lens.search_by_url(url)
            if result is None:
                await reply_message.edit("Couldn't find anything or there was an issue with the image.")
            else:
                cum = "**Results**:\n\n"
                match = result.get('match')
                if match:
                    match = match.replace("[", "").replace("]", "")
                    cum += f"**Best Match**: [{match['title']}]({match['pageURL']})\n\n"
                    cum += "**Similar Results**:\n\n"
                similar = result.get('similar')
                if similar:
                    try:
                        for r in similar[:5]:
                            title = r.get('title')
                            if title:
                                title = title.replace("[", "").replace("]", "")
                                cum += f"[{title}]({r['pageURL']})\n"
                    except:
                        for r in similar:
                            title = r.get('title')
                            if title:
                                title = title.replace("[", "").replace("]", "")
                                cum += f"[{title}]({r['pageURL']})\n"
                await reply_message.edit(cum)
        except KeyError:
            pass
        except Exception as e:
            LOGGER.error(traceback.format_exc())
            await reply_message.edit(f"Error: {str(e)}")

    reply_message = await event.get_reply_message()

    if not reply_message or not reply_message.media:
        return await event.reply("Please reply to a sticker, photo, or an image to search it!")

    media = reply_message.media
    if isinstance(media, MessageMediaPhoto) or (media.document and media.document.mime_type.startswith("image/")):
        wait = await event.reply("waito...")
        url = await upload(reply_message)
        await process_and_reply(wait, url)
    else:
        await event.reply("Video and animated stickers cannot be reversed. Please reply with an image.")
