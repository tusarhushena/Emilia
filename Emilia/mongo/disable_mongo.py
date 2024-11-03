from Emilia import db

disable = db.disable


async def disable_db(chat_id, disable_arg):
    disable_data = await disable.find_one({"chat_id": chat_id})
    if disable_data is None:

        await disable.insert_one(
            {
                "chat_id": chat_id,
                "disabled_items": [disable_arg],
                "disabledel": False,
            }
        )
    else:
        await disable.update_one(
            {"chat_id": chat_id},
            {"$addToSet": {"disabled_items": disable_arg}},
            upsert=True,
        )


async def enable_db(chat_id, enable_arg):
    disable_data = await disable.find_one({"chat_id": chat_id})
    if disable_data is not None:
        disabled_list = await get_disabled(chat_id)
        if enable_arg in disabled_list:
            await disable.update_one(
                {"chat_id": chat_id},
                {"$pull": {"disabled_items": enable_arg}},
                upsert=True,
            )


async def get_disabled(chat_id) -> list:
    disable_data = await disable.find_one({"chat_id": chat_id})

    if disable_data is not None:
        return disable_data["disabled_items"]
    else:
        return []


async def disabledel_db(chat_id, disabledel):
    disable_data = await disable.find_one({"chat_id": chat_id})
    if disable_data is not None:
        await disable.update_one(
            {"chat_id": chat_id}, {"$set": {"disabledel": disabledel}}, upsert=True
        )
    else:
        await disable.insert_one(
            {
                "chat_id": chat_id,
                "disabled_items": [],
                "disabledel": disabledel,
            }
        )


async def get_disabledel(chat_id) -> bool:
    disable_data = await disable.find_one({"chat_id": chat_id})
    if disable_data is not None:
        return disable_data["disabledel"]
    else:
        return False
