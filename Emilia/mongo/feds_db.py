from Emilia import db

feds = db.feds
fbans = db.fbans
fsubs = db.fsubs
fadmins = db.fadmins


async def new_fed(owner_id: int, fed_id, fedname):
    await feds.update_one(
        {"owner_id": owner_id},
        {
            "$set": {
                "fed_id": fed_id,
                "fedname": fedname,
                "fedadmins": [],
                "flog": None,
                "chats": [],
                "report": True,
            }
        },
        upsert=True,
    )


async def del_fed(fed_id):
    await feds.delete_one({"fed_id": fed_id})
    await fbans.delete_one({"fed_id": fed_id})
    await fsubs.delete_one({"fed_id": fed_id})


async def transfer_fed(owner_id: int, user_id: int):
    _fed = await feds.find_one({"owner_id": owner_id})
    if _fed:
        await feds.update_one(
            {"fed_id": _fed["fed_id"]}, {"$set": {"owner_id": user_id}}, upsert=True
        )


async def rename_fed(fed_id, fname):
    _fed = await feds.find_one({"fed_id": fed_id})
    if _fed:
        await feds.update_one(
            {"fed_id": fed_id}, {"$set": {"fedname": fname}}, upsert=True
        )


async def chat_join_fed(fed_id, chat_id: int):
    _fed = await feds.find_one({"fed_id": fed_id})
    if _fed:
        chats = _fed["chats"]
        chats.append(chat_id)
        await feds.update_one(
            {"fed_id": fed_id}, {"$set": {"chats": chats}}, upsert=True
        )


async def user_demote_fed(fed_id, user_id: int):
    _fed = await feds.find_one({"fed_id": fed_id})
    if _fed:
        fedadmins = _fed["fedadmins"]
        fedadmins.remove(user_id)
        await feds.update_one(
            {"fed_id": fed_id}, {"$set": {"fedadmins": fedadmins}}, upsert=True
        )


async def user_join_fed(fed_id, user_id: int):
    _fed = await feds.find_one({"fed_id": fed_id})
    if _fed:
        fedadmins = _fed["fedadmins"]
        fedadmins.append(user_id)
        await feds.update_one(
            {"fed_id": fed_id}, {"$set": {"fedadmins": fedadmins}}, upsert=True
        )


async def chat_leave_fed(fed_id, chat_id):
    _fed = await feds.find_one({"fed_id": fed_id})
    if _fed:
        chats = _fed["chats"]
        chats.remove(chat_id)
        await feds.update_one(
            {"fed_id": fed_id}, {"$set": {"chats": chats}}, upsert=True
        )


async def get_fed_reason(fed_id):
    _fed = await feds.find_one({"fed_id": fed_id})
    if _fed:
        return _fed["report"]
    return False


async def set_fed_reason(fed_id, mode):
    await feds.update_one({"fed_id": fed_id}, {"$set": {"report": mode}}, upsert=True)


async def fban_user(fed_id, user_id: str, firstname, lastname, reason, time: str):
    _fban = await fbans.find_one({"fed_id": fed_id})
    if _fban:
        f_bans = _fban["fbans"]
    else:
        f_bans = {}
    f_bans[str(user_id)] = [firstname, lastname, reason, time]
    await fbans.update_one({"fed_id": fed_id}, {"$set": {"fbans": f_bans}}, upsert=True)


async def unfban_user(fed_id, user_id):
    _fban = await fbans.find_one({"fed_id": fed_id})
    if _fban:
        f_bans = _fban["fbans"]
    else:
        f_bans = {}
    if f_bans[str(user_id)]:
        del f_bans[str(user_id)]
    await fbans.update_one({"fed_id": fed_id}, {"$set": {"fbans": f_bans}}, upsert=True)


async def get_user_owner_fed_full(owner_id):
    _all_feds = await feds.find_one({"owner_id": owner_id})
    if _all_feds:
        return _all_feds["fed_id"], _all_feds["fedname"]
    return None


async def search_fed_by_id(fed_id):
    _x_fed = await feds.find_one({"fed_id": fed_id})
    if _x_fed:
        return _x_fed
    return None


async def get_len_fbans(fed_id):
    _x_fbans = await fbans.find_one({"fed_id": fed_id})
    if _x_fbans:
        return len(_x_fbans.get("fbans"))
    return 0


async def get_all_fbans(fed_id):
    _x_fbans = await fbans.find_one({"fed_id": fed_id})
    if _x_fbans:
        return _x_fbans.get("fbans")
    return None


async def get_chat_fed(chat_id):
    _x = feds.find({})
    async for x in _x:
        if "chats" in x:
            if chat_id in x["chats"]:
                return_able = x["fed_id"]
                if len(return_able) == 0:
                    return None
                return return_able
    return None


async def get_fban_user(fed_id, user_id: str):
    _x_data = await fbans.find_one({"fed_id": fed_id})
    if _x_data:
        _xx_data = _x_data.get("fbans")
        if _xx_data:
            __xxx_data = _xx_data.get(str(user_id))
            if __xxx_data:
                return True, __xxx_data[2], __xxx_data[3]
    return False, None, None


async def search_user_in_fed(fed_id, user_id: int):
    _x = await feds.find_one({"fed_id": fed_id})
    if _x:
        _admins = _x.get("fedadmins")
        if _admins and len(_admins) > 0:
            if user_id in _admins:
                return True
    return False


async def user_feds_report(user_id: int):
    _x = await feds.find_one({"owner_id": user_id})
    if _x:
        return _x["report"]
    return True


async def set_feds_setting(user_id: int, mode):
    await feds.update_one(
        {"owner_id": user_id}, {"$set": {"report": mode}}, upsert=True
    )


async def get_all_fed_admins(fed_id):
    _fed = await feds.find_one({"fed_id": fed_id})
    x_admins = _fed["fedadmins"]
    x_owner = _fed["owner_id"]
    x_admins.append(x_owner)
    return x_admins


async def get_fed_log(fed_id):
    _fed = await feds.find_one({"fed_id": fed_id})
    if _fed:
        return _fed["flog"]
    return False


async def get_all_fed_chats(fed_id):
    _fed = await feds.find_one({"fed_id": fed_id})
    return _fed.get("chats")


async def sub_fed(fed_id: str, my_fed: str):
    x_mysubs = await fsubs.find_one({"fed_id": my_fed})
    if x_mysubs:
        my_subs = x_mysubs["my_subs"]
    else:
        my_subs = []
    my_subs.append(fed_id)
    my_subs = list(set(my_subs))
    await fsubs.update_one(
        {"fed_id": my_fed}, {"$set": {"my_subs": my_subs}}, upsert=True
    )
    x_fedsubs = await fsubs.find_one({"fed_id": fed_id})
    if x_fedsubs:
        fed_subs = x_fedsubs["fed_subs"]
    else:
        fed_subs = []
    fed_subs.append(my_fed)
    fed_subs = list(set(fed_subs))
    await fsubs.update_one(
        {"fed_id": fed_id}, {"$set": {"fed_subs": fed_subs}}, upsert=True
    )


async def get_all_subscribed_feds(fed_id):
    x_mysubs = await fsubs.find_one({"fed_id": fed_id})
    if x_mysubs:
        return x_mysubs.get("my_subs") or []
    return []


async def unsub_fed(fed_id: str, my_fed: str):
    x_mysubs = await fsubs.find_one({"fed_id": my_fed})
    if x_mysubs:
        my_subs = x_mysubs["my_subs"]
    else:
        my_subs = []
    if fed_id in my_subs:
        my_subs.remove(fed_id)
    await fsubs.update_one(
        {"fed_id": my_fed}, {"$set": {"my_subs": my_subs}}, upsert=True
    )
    x_fedsubs = await fsubs.find_one({"fed_id": fed_id})
    if x_fedsubs:
        fed_subs = x_fedsubs["fed_subs"]
    else:
        fed_subs = []
    if my_fed in fed_subs:
        fed_subs.remove(my_fed)
    await fsubs.update_one(
        {"fed_id": fed_id}, {"$set": {"fed_subs": fed_subs}}, upsert=True
    )


async def get_my_subs(fed_id):
    x_mysubs = await fsubs.find_one({"fed_id": fed_id})
    if x_mysubs:
        return x_mysubs.get("my_subs") or []
    return []


async def get_fed_subs(fed_id):
    x_fedsubs = await fsubs.find_one({"fed_id": fed_id})
    if x_fedsubs:
        return x_fedsubs.get("fed_subs") or []
    return []


async def add_fname(user_id, fname):
    await fadmins.update_one(
        {"user_id": user_id}, {"$set": {"fname": fname}}, upsert=True
    )


async def get_fname(user_id):
    x = await fadmins.find_one({"user_id": user_id})
    if x:
        return x["fname"]
    return None


async def set_fed_log(fed_id: str, chat_id=None):
    await feds.update_one({"fed_id": fed_id}, {"$set": {"flog": chat_id}}, upsert=True)


async def get_all_fed_admin_feds(user_id):
    admin = []
    fed = {}
    for x in await feds.find():
        if user_id in x.get("fedadmins"):
            admin.append(x.get("fed_id"))
    owner = await feds.find_one({"owner_id": user_id})
    if owner:
        fed["owner"] = owner["fed_id"]
    if admin:
        fed["admin"] = admin
    return fed


async def get_all_fed_admin(user_id):
    admin = []
    for x in await feds.find():
        if user_id in x.get("fedadmins"):
            admin.append(x.get("fed_id"))

    return admin


async def get_fed_name(fed_id):
    _fed = await feds.find_one({"fed_id": fed_id})
    if _fed:
        return _fed.get("fedname")
    return None


async def quietfed(chat_id=None, argument: bool = False):
    await feds.update_one(
        {"chat_id": chat_id}, {"$set": {"quiet": argument}}, upsert=True
    )
