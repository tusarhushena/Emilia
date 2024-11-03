from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from Emilia import pgram
from Emilia.helper.chat_status import isUserAdmin
from Emilia.mongo.warnings_mongo import remove_warn


@Client.on_callback_query(filters.create(lambda _, __, query: "warn_" in query.data))
async def warn_remove_callback(client: Client, callback_query: CallbackQuery):
    user_id = int(callback_query.data.split("_")[1])
    warn_id = int(callback_query.data.split("_")[2])
    chat_id = callback_query.message.chat.id
    from_user = callback_query.from_user.id
    admin_mention = callback_query.from_user.mention

    if not await isUserAdmin(
        message=callback_query.message, user_id=from_user, chat_id=chat_id, silent=True
    ):
        return await callback_query.answer(text="You're not an admin.")

    user_data = await pgram.get_users(user_ids=user_id)
    await remove_warn(chat_id, user_id, warn_id)
    await callback_query.message.reply(f"Admin {admin_mention} has removed {user_data.mention}'s warning.")
    await callback_query.message.delete()

    return
