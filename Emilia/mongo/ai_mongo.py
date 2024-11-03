from Emilia import db

chatbotdb1 = db.ai


async def addchat_bot1(chat_id: int):
    await chatbotdb1.insert_one({"chat_id": chat_id})


async def rmchat_bot1(chat_id: int):
    chat = await chatbotdb1.find_one({"chat_id": chat_id})
    if chat:
        await chatbotdb1.delete_one({"chat_id": chat_id})
