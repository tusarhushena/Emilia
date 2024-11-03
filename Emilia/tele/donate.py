from Emilia.custom_filter import register
from telethon import Button

@register(pattern="donate")
async def handle_donate(event):
    message = "🌟 Thank you for considering a donation! 🌟\n\n"
    message += "Your support helps us continue providing great services.\n\n"
    message += "To donate, please click on the button below.\n"
    message += "We appreciate your generosity! ❤️"
    button = [Button.url("Donate", "https://t.me/Elf_Robot/donation")]
    await event.reply(message, buttons=button)