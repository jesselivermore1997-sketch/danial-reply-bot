from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = 33828680
API_HASH = "11b34dc04686e99af9548b06c80ed2b0"

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("SESSION STRING:")
    print(client.session.save())
