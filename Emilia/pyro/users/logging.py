from pyrogram import Client, enums, filters

from Emilia.mongo.users_mongo import add_chat, add_user


@Client.on_message(filters.all & filters.group & ~filters.user(777000), group=1)
async def logger(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    await add_chat(chat_id, chat_title)

    if message.from_user:
        user_id = message.from_user.id
        username = message.from_user.username
        await add_user(user_id, username, chat_id, chat_title)

    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username

        await add_user(user_id, username, chat_id, chat_title)

    if message.forward_from:
        user_id = message.forward_from.id
        username = message.forward_from.username

        await add_user(user_id, username, Forwared=True)


@Client.on_message(filters.all & ~filters.group & ~filters.user(777000))
async def pvtlogger(client, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        username = message.from_user.username or None
        await add_user(message.from_user.id, username, Forwared=True)
