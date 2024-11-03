from Emilia import db

locks = db.locks


async def lock_db(chat_id, lock_item):
    locks_data = await locks.find_one({"chat_id": chat_id})

    if locks_data is None:
        await locks.insert_one(
            {
                "chat_id": chat_id,
                "locked": [lock_item],
                "lockwarns": True,
                "allow_list": [],
            }
        )
    else:
        await locks.update_one(
            {"chat_id": chat_id}, {"$addToSet": {"locked": lock_item}}
        )


async def get_locks(chat_id) -> list:
    locks_data = await locks.find_one({"chat_id": chat_id})

    if locks_data is not None:
        return locks_data["locked"]
    else:
        return []


async def unlock_db(chat_id, locked_item):
    locks_data = await locks.find_one({"chat_id": chat_id})
    if locks_data is not None:
        await locks.update_one({"chat_id": chat_id}, {"$pull": {"locked": locked_item}})


async def lockwarns_db(chat_id) -> bool:
    locks_data = await locks.find_one({"chat_id": chat_id})

    if locks_data is not None:
        return locks_data["lockwarns"]
    else:
        return True


async def set_lockwarn_db(chat_id, warn_args):
    locks_data = await locks.find_one({"chat_id": chat_id})
    if locks_data is not None:
        await locks.update_one(
            {"chat_id": chat_id},
            {
                "$set": {"lockwarns": warn_args},
            },
            upsert=True,
        )
    else:
        await locks.insert_one(
            {
                "chat_id": chat_id,
                "locked": [],
                "lockwarns": warn_args,
                "allow_list": [],
            }
        )


async def allowlist_db(chat_id, allowlist_arg):
    locks_data = await locks.find_one({"chat_id": chat_id})
    if locks_data is not None:
        await locks.update_one(
            {"chat_id": chat_id}, {"$addToSet": {"allow_list": allowlist_arg}}
        )
    else:
        await locks.insert_one(
            {
                "chat_id": chat_id,
                "locked": [],
                "lockwarns": True,
                "allow_list": [allowlist_arg],
            }
        )


async def rmallow_db(chat_id, allow_arg):
    locks_data = await locks.find_one({"chat_id": chat_id})
    if locks_data is not None:
        await locks.update_one(
            {"chat_id": chat_id}, {"$pull": {"allow_list": allow_arg}}, upsert=True
        )


async def rmallowall_db(chat_id):
    locks_data = await locks.find_one({"chat_id": chat_id})
    if locks_data is not None:
        await locks.update_one(
            {"chat_id": chat_id}, {"$set": {"allow_list": []}}, upsert=True
        )


async def get_allowlist(chat_id) -> list:
    locks_data = await locks.find_one({"chat_id": chat_id})
    if locks_data is not None:
        return locks_data["allow_list"]
    else:
        return []
