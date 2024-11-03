from Emilia import db

blocklists = db.blocklists


async def add_blocklist_db(chat_id, blocklist_text, blocklist_reason):
    blocklist_data = await blocklists.find_one({"chat_id": chat_id})

    if blocklist_data is None:
        await blocklists.insert_one(
            {
                "chat_id": chat_id,
                "blocklist_text": [
                    {
                        "blocklist_text": blocklist_text,
                        "blocklist_reason": blocklist_reason,
                    }
                ],
                "blocklist_mode": {
                    "blocklist_mode": 1,
                    "blocklist_time": None,
                    "blocklist_default_reason": None,
                },
                "blocklistdelete": True,
                "blocklist_default_reason": None,
            }
        )
    else:
        BLOCKLIST_LIST = blocklist_data["blocklist_text"]
        BLOCKLIST_TEXT_LIST = []
        BLOCKLIST_REASON_LIST = []
        for blacklist_obj in BLOCKLIST_LIST:
            BLOCKLIST_TEXT_LIST.append(blacklist_obj["blocklist_text"])
            BLOCKLIST_REASON_LIST.append(blacklist_obj["blocklist_reason"])

        if blocklist_text not in BLOCKLIST_TEXT_LIST:
            await blocklists.update_one(
                {"chat_id": chat_id},
                {
                    "$push": {
                        "blocklist_text": {
                            "blocklist_text": blocklist_text,
                            "blocklist_reason": blocklist_reason,
                        }
                    }
                },
                upsert=True,
            )

        for reason_list in BLOCKLIST_LIST:
            text = reason_list["blocklist_text"]
            reason = reason_list["blocklist_reason"]
            if text == blocklist_text:
                if reason != blocklist_reason:
                    await blocklists.update_one(
                        {
                            "chat_id": chat_id,
                            "blocklist_text.blocklist_text": blocklist_text,
                        },
                        {
                            "$set": {
                                "blocklist_text.$.blocklist_reason": blocklist_reason
                            }
                        },
                        upsert=True,
                    )


async def rmblocklist_db(chat_id, blocklist_name):
    blocklist_data = await blocklists.find_one({"chat_id": chat_id})

    if blocklist_data is not None:
        await blocklists.update_one(
            {"chat_id": chat_id, "blocklist_text.blocklist_text": blocklist_name},
            {"$pull": {"blocklist_text": {"blocklist_text": blocklist_name}}},
        )


async def unblocklistall_db(chat_id):
    await blocklists.update_one({"chat_id": chat_id}, {"$set": {"blocklist_text": []}})


async def get_blocklist(chat_id) -> list:
    blocklist_data = await blocklists.find_one({"chat_id": chat_id})

    if blocklist_data is not None:
        BLOCKLIST = blocklist_data["blocklist_text"]
        return BLOCKLIST


async def get_blocklist_reason(chat_id, blocklist_text):
    blocklist_data = await blocklists.find_one(
        {"chat_id": chat_id, "blocklist_text.blocklist_text": blocklist_text}
    )
    if blocklist_data is not None:
        blocklist_text_array = blocklist_data["blocklist_text"]
        for bl_data in blocklist_text_array:
            bl_text = bl_data["blocklist_text"]
            if bl_text == blocklist_text:
                blocklist_reason = bl_data["blocklist_reason"]
                return blocklist_reason
        else:
            return None
    else:
        return None


async def blocklistMessageDelete(chat_id, blocklistdelete):
    blocklist_data = await blocklists.find_one({"chat_id": chat_id})

    if blocklist_data is not None:
        await blocklists.update_one(
            {"chat_id": chat_id},
            {"$set": {"blocklistdelete": blocklistdelete}},
            upsert=True,
        )
    else:
        await blocklists.insert_one(
            {
                "chat_id": chat_id,
                "blocklist_text": [],
                "blocklist_mode": {"blocklist_mode": 1, "blocklist_time": None},
                "blocklistdelete": True,
                "blocklist_default_reason": None,
            }
        )


async def getblocklistMessageDelete(chat_id) -> bool:
    blocklist_data = await blocklists.find_one({"chat_id": chat_id})
    if blocklist_data is not None:
        return blocklist_data["blocklistdelete"]
    else:
        return True


async def setblocklistmode(chat_id, blocklist_mode, blocklist_time=None):
    blocklist_data = await blocklists.find_one({"chat_id": chat_id})

    if blocklist_data is not None:
        await blocklists.update_one(
            {"chat_id": chat_id},
            {
                "$set": {
                    "blocklist_mode": {
                        "blocklist_mode": blocklist_mode,
                        "blocklist_time": blocklist_time,
                    }
                }
            },
            upsert=True,
        )
    else:
        await blocklists.insert_one(
            {
                "chat_id": chat_id,
                "blocklist_text": [],
                "blocklist_mode": {
                    "blocklist_mode": blocklist_mode,
                    "blocklist_time": blocklist_time,
                },
                "blocklistdelete": True,
                "blocklist_default_reason": None,
            }
        )


async def getblocklistmode(chat_id):
    blocklist_data = await blocklists.find_one({"chat_id": chat_id})

    if blocklist_data is not None:
        blocklist_mode = blocklist_data["blocklist_mode"]["blocklist_mode"]
        blocklist_time = blocklist_data["blocklist_mode"]["blocklist_time"]
        blocklist_default_reason = blocklist_data["blocklist_default_reason"]

        return (blocklist_mode, blocklist_time, blocklist_default_reason)

    else:
        blocklist_mode = 1
        blocklist_time = None
        blocklist_default_reason = None

        return (blocklist_mode, blocklist_time, blocklist_default_reason)


async def setblocklistreason_db(chat_id, reason):
    blocklist_data = await blocklists.find_one({"chat_id": chat_id})

    if blocklist_data is not None:
        await blocklists.update_one(
            {"chat_id": chat_id},
            {"$set": {"blocklist_default_reason": reason}},
            upsert=True,
        )
    else:
        await blocklists.insert_one(
            {
                "chat_id": chat_id,
                "blocklist_text": [],
                "blocklist_mode": {"blocklist_mode": 1, "blocklist_time": None},
                "blocklistdelete": True,
                "blocklist_default_reason": reason,
            }
        )
