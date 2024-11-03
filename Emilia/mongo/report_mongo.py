from Emilia import db

reports = db.reports


async def reports_db(chat_id: int, report_arg: bool):
    report_data = await reports.find_one({"chat_id": chat_id})

    if report_data is None:
        await reports.insert_one({"chat_id": chat_id, "reports": report_arg})
    else:
        await reports.update_one(
            {"chat_id": chat_id}, {"$set": {"reports": report_arg}}, upsert=True
        )


async def get_report(chat_id: int) -> bool:
    report_data = await reports.find_one({"chat_id": chat_id})

    if report_data is not None:
        return report_data["reports"]
    else:
        return True
