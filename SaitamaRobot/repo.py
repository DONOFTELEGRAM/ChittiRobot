from pyrogram import filters

from SaitamaRobot import pgram as app, BOT_USERNAME
from SaitamaRobot.utils.errors import capture_err
from SaitamaRobot.utils.http import get


@app.on_message(filters.command("repo", f"repo@{BOT_USERNAME}") & ~filters.edited)
@capture_err
async def repo(_, message):
    users = await get(
        "https://api.github.com/repos/itzzzyashu/RajniiRobot/contributors"
    )
    list_of_users = ""
    count = 1
    for user in users:
        list_of_users += (
            f"**{count}.** [{user['login']}]({user['html_url']})\n"
        )
        count += 1

    text = f"""[Updates](https://t.me/RajniUpdates) | [Support](https://t.me/RajniSupport)
```----------------
| Contributors |
----------------```
{list_of_users}"""
    await app.send_message(
        message.chat.id, text=text, disable_web_page_preview=True)
