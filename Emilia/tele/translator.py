# DONE: Translator

from gpytranslate import SyncTranslator
from mtranslate import translate

from Emilia import SUPPORT_CHAT
from Emilia.custom_filter import register
from Emilia.helper.disable import disable


@register(pattern="translate", disable=True)
@disable
async def trans(event):
    reply = await event.get_reply_message()
    if reply:
        reply = reply.text
    else:
        reply = event.text.split(None, 1)[1]
        if not reply:
            await event.reply("Reply to a text to translate it!")
            return

    try:
        meow = translate(reply)
        await event.reply(meow)
    except BaseException:
        await event.reply(
            f"Cannot be translated due to some issue. Try again or report at @{SUPPORT_CHAT}"
        )


trans = SyncTranslator()


@register(pattern="tr")
async def _(event):
    reply_msg = await event.get_reply_message()
    if not reply_msg:
        await event.reply("Reply to a text to translate it!")
        return
    if reply_msg.message:
        to_translate = reply_msg.message
    elif reply_msg.text:
        to_translate = reply_msg.text
    try:
        args = event.text.split()[1].lower()
        if "//" in args:
            source = args.split("//")[0]
            dest = args.split("//")[1]
        else:
            source = trans.detect(to_translate)
            dest = args
    except IndexError:
        source = trans.detect(to_translate)
        dest = "en"
    translation = (trans(to_translate, sourcelang=source, targetlang=dest))["text"]
    reply = f"Translated from {source} to {dest}\n\n{translation}"

    await event.reply(reply)
