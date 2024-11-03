from Emilia import BOT_NAME


__mod_name__ = "Topics"

__help__ = f"""
Manage your topic settings through {BOT_NAME}!

Topics introduce lots of small differences to normal supergroups; this could affect how you would usually manage your chat.

You can use the bot to create, rename, close and delete your topics.

**Admin commands**:

• /newtopic <name>: Create a new topic.
• /renametopic <name>: Rename the current topic. (For general topic, please reply to a message in order to rename it.)
• /opentopic <topic id>: Opens the closed topic of which id was given.
• /closetopic <topic id>: Closes the desired topic.
• /deletetopic <topic id>: Delete desired topic, and all the topic messages. Cannot be undone!
"""
