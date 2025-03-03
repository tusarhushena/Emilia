from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Emilia import custom_filter, BOT_NAME, TOKEN, ORIGINAL_EVENT_LOOP, SUPPORT_CHAT, UPDATE_CHANNEL, START_PIC
from Emilia.anime.bot import get_anime, get_recommendations, auth_link_cmd, logout_cmd
from Emilia.pyro.connection.connect import connectRedirect
from Emilia.pyro.greetings.captcha.button_captcha import buttonCaptchaRedirect
from Emilia.pyro.greetings.captcha.text_captcha import textCaptchaRedirect
from Emilia.pyro.notes.private_notes import note_redirect
from Emilia.pyro.rules.rules import rulesRedirect
from Emilia.utils.decorators import *
from Emilia.tele.clone import startpic

START_TEXT = """
Welcome to [{} :3]({})

This bot give varieties of features such as
➩ Group Management
➩ Spammer Protection
➩ Fun like chatbot
➩ Clone, Ranking, AI System
➩ Anime Loaded Modules

Use the buttons buttons or /help to checkout even more!
"""


@Client.on_message(custom_filter.command(commands="start"))
@leavemute
@rate_limit(40, 60)
async def starttt(client, message):
    if len(message.text.split()) == 1:
        if message.chat.type == ChatType.PRIVATE:
            buttons = [
                [InlineKeyboardButton("Help", callback_data="help_back")],
                [
                    InlineKeyboardButton(
                        "Support 💬", url=f"https://t.me/{SUPPORT_CHAT}"
                    ),
                    InlineKeyboardButton("News 📢", url=f"https://t.me/{UPDATE_CHANNEL}"),
                ],
                [InlineKeyboardButton("How to Clone Management Bot 🤖", callback_data="clone_help")],
                [InlineKeyboardButton("How to Clone Music Bot 🤖", url="https://Cloning_Music_Bot")],
            ]
            
            await message.reply_text(
                START_TEXT.format(BOT_NAME, START_PIC),
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=False,
            )

        elif message.chat.type != ChatType.PRIVATE:
            await message.reply("Hey there, ping me in my PM to get help!")

    if len(message.text.split()) > 1:
        user = message.from_user.id
        chat = message.chat.id
        deep_cmd_list = (message.text.split()[1]).split("_")

        # Captcha Redirect Implementation
        if startCheckQuery(message, StartQuery="captcha"):
            await buttonCaptchaRedirect(message)
            await textCaptchaRedirect(message)

        # Private Notes Redirect Implementation
        elif startCheckQuery(message, StartQuery="note"):
            await note_redirect(message)

        # Connection Redirect Implementation
        elif startCheckQuery(message, StartQuery="connect"):
            await connectRedirect(message)

        # Rules Redirect Implementation
        elif startCheckQuery(message, StartQuery="rules"):
            await rulesRedirect(message)

        elif startCheckQuery(message, StartQuery="anihelp"):
            await help_(client, message)

        elif startCheckQuery(message, StartQuery="auth"):
            await auth_link_cmd(client, message)

        elif startCheckQuery(message, StartQuery="logout"):
            await logout_cmd(client, message)

        elif deep_cmd_list[0] == "des":
            try:
                req = deep_cmd_list[3]
            except IndexError:
                req = "desc"
            pic, result = await get_additional_info(
                deep_cmd_list[2], deep_cmd_list[1], req
            )
            await client.send_photo(chat, pic)
            try:
                await client.send_message(
                    chat, result.replace("~!", "").replace("!~", "")
                )
            except (TypeError, AttributeError):
                await client.send_message(chat, "No description available!!!")

        elif deep_cmd_list[0] == "anime":
            auth = False
            if await AUTH_USERS.find_one({"id": user}):
                auth = True
            result = await get_anime(
                {"id": int(deep_cmd_list[1])}, user=user, auth=auth
            )
            pic, msg = result[0], result[1]
            buttons = get_btns("ANIME", result=result, user=user, auth=auth)
            await client.send_photo(chat, pic, caption=msg, reply_markup=buttons)

        elif deep_cmd_list[0] == "anirec":
            result = await get_recommendations(deep_cmd_list[1])
            await client.send_message(user, result, disable_web_page_preview=True)

        elif (message.text.split()[1]).split("_", 1)[0] == "code":
            if not os.environ.get("ANILIST_REDIRECT_URL"):
                return
            qry = (message.text.split()[1]).split("_", 1)[1]
            k = await AUTH_USERS.find_one({"_id": ObjectId(qry)})
            await code_cmd(k["code"], message)


def startCheckQuery(message, StartQuery=None) -> bool:
    if (
        StartQuery in message.text.split()[1].split("_")[0]
        and message.text.split()[1].split("_")[0] == StartQuery
    ):
        return True
    else:
        return False

button = [[InlineKeyboardButton("Clone Commands", callback_data="bot_clone")]]

@Client.on_callback_query()
async def callback_query_handler(client, callback_query):
    if callback_query.data == "clone_help":  
        await callback_query.message.reply_text(clone_help, reply_markup=InlineKeyboardMarkup(button))
        await callback_query.message.delete()
        return
    if callback_query.data == "bot_clone":   
        await callback_query.message.reply_text(help_text, disable_web_page_preview=True)
        await callback_query.message.delete()
        return


clone_help = """
Harry Clones are exact replicas of @HarryCloneBot but with a personalized name and profile picture, ensuring enhanced performance and stability.

Clones inherit all functionalities, updates, and database entries from the original bot. When switching between clones in a group, there's no need to reconfigure settings.

**To create a clone**:
1. Open @BotFather.
2. Initiate a chat with @BotFather and type /newbot.
3. Choose a name for your clone.
4. Select a username for your clone.
5. Copy the API token provided by @BotFather.
6. Send the API token to Harry Cloner via private message using `/clone [apitokenhere]`. Ensure to remove '[ ]'.
7. You're all set!

To modify the profile picture of your clone, send /setuserpic to @BotFather, choose the clone, and upload the new image.

**CAUTION**: When adding a clone to a group, remember to assign it administrator privileges!
"""

help_text = """
Nowadays, many people use foreign bots to manage their groups. But this can be risky as the bot owner can misuse your data.
To solve this issue, we have introduced the clone feature. Without the need for any coding knowledge, database, hosting, or anything else, this feature allows you to clone @Elf_Robot to your own bots and manage your group without any privacy concerns.

**Clone Commands:**

• /clone `[bottoken]`: Clones @HarryCloneBot to your provided bot. Make sure to remove the square brackets.
• /deleteclone `[bottoken]`: Deletes the cloned bot from our server.
• /setstartpic `[picurl]`: Sets the start pic for your cloned bot.
• /broadcast `-flag [reply]`: Broadcasts the replied message to all the groups where the cloned bot is present.

Flags available for broadcast:
- `-all`: Broadcast to all groups and users.
- `-chats`: Broadcast to all groups only.
- `-users`: Broadcast to all users only.

Example:
- `/broadcast -all [reply to message]`


**Note:** The bot will get restarted every 12 hours and it uses the same database as the main bot. Please do not use this feature for illegal purposes. We will not be responsible for any misuse.

PS: If you need any help, feel free to ask in our support group [here.](https://t.me/DeadlineTechSupport) I have created this feature with my heart, and it took a lot of time and effort. So, please don't hesitate to /donate to keep this feature alive.
In future, we might close this feature and make it premium. So, use it now and enjoy :3
"""
