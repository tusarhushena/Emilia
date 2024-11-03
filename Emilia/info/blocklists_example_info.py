__mod_name__ = "Blocklist Command Examples"

__hidden__ = True

__help__ = """
If you're still curious as to how blocklists work, here are some examples you can copy.

**Example blocklist commands**:
• Automatically warn users who say blocklisted words:
-> `/blocklistmode warn`

• Override the blocklist mode for a single filter. Users that says 'boo' will get a muted for 6 hours, instead of the blocklist action:
-> `/addblocklist boo Don't scare the ghosts! {tmute 6h}`

• Add a full sentence to the blocklist. This would delete any message containing 'the admins suck':
-> `/addblocklist "the admins suck" Respect your admins!`

• Add multiple blocklist entries at once by separating wrapping in brackets, and separating with commas:
-> `/addblocklist (hi, hey, hello) Stop saying hello!`

• Stop any `bit.ly` links using the * shortcut to match any character:
-> `/addblocklist "bit.ly/*" We dont like shorteners!`

• Stop any `bit.ly` links followed by exactly three characters, to catch `bit.ly/hey`, but not `bit.ly/abcd`:
-> `/addblocklist "bit.ly/???" We dont like 3 letter shorteners!`

• Stop people sending zip files, by blocklisting `file:*.zip`:
-> `/addblocklist "file:*.zip" zip files are not allowed here.`

• Stop any 🖕 emoji, or any stickers related to it:
-> `/addblocklist 🖕 This emoji is not allowed here.`
"""
