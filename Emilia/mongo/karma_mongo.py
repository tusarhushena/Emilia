from Emilia import db

karmadb = db.karma


async def get_karmas_count() -> dict:
    chats_count = 0
    karmas_count = 0
    async for chat in karmadb.find({"chat_id": {"$lt": 0}}):
        for i in chat["karma"]:
            karma_ = chat["karma"][i]["karma"]
            if karma_ > 0:
                karmas_count += karma_
        chats_count += 1
    return {"chats_count": chats_count, "karmas_count": karmas_count}


m = db.chatlevels


async def user_global_karma(user_id) -> int:
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$chat_id", "highest_points": {"$max": "$points"}}},
        {"$sort": {"highest_points": -1}},
        {"$limit": 1},
    ]
    result = await m.aggregate(pipeline).to_list(1)
    return result[0]["highest_points"]


async def is_karma_on(chat_id: int) -> bool:
    chat = await karmadb.find_one({"chat_id_toggle": chat_id})
    if not chat:
        return False
    return True


async def karma_on(chat_id: int):
    is_karma = await is_karma_on(chat_id)
    if is_karma:
        return
    return await karmadb.insert_one({"chat_id_toggle": chat_id})


async def karma_off(chat_id: int):
    is_karma = await is_karma_on(chat_id)
    if not is_karma:
        return
    return await karmadb.delete_one({"chat_id_toggle": chat_id})
