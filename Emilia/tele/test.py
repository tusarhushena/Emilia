from Emilia.custom_filter import register
from Emilia.utils.decorators import *


@register(pattern="test")
@rate_limit(3, 60)
async def test(event):
    await event.reply("test")
