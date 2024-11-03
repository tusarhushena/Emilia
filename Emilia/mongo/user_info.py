from Emilia import db

infodb = db.user_info


async def set_me(user_id: int, info: str):
    return await infodb.update_one(
        {"user_id": user_id}, {"$set": {"info": info}}, upsert=True
    )


async def get_me(user_id: int):
    user = await infodb.find_one({"user_id": user_id})
    if user:
        return user.get("info")
    return None


async def set_bio(user_id: int, bio: str):
    return await infodb.update_one(
        {"user_id": user_id}, {"$set": {"bio": bio}}, upsert=True
    )


async def get_bio(user_id: int):
    user = await infodb.find_one({"user_id": user_id})
    if user:
        return user.get("bio")
    return None
