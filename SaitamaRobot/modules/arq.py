from pyrogram import filters
from SaitamaRobot import SUPPORT_CHAT
from SaitamaRobot import ARQ_API_URL, pgram as app, arq, dispatcher



async def arq_stats(_, message):
    data = await arq.stats()
    if not data.ok:
        return await message.reply_text(data.result)
    data = data.result
    uptime = data.uptime
    requests = data.requests
    cpu = data.cpu
    server_mem = data.memory.server
    api_mem = data.memory.api
    disk = data.disk
    platform = data.platform
    python_version = data.python
    users = data.users
    bot = data.bot
    statistics = f"""
**Uptime:** `{uptime}`
**Requests Since Uptime:** `{requests}`
**CPU:** `{cpu}`
**Memory:**
    **Total Used:** `{server_mem}`
    **API:** `{api_mem}`
**Disk:** `{disk}`
**Platform:** `{platform}`
**Python:** `{python_version}`
**Users:** `{users}`
**Bot:** {bot}
**Address:** {ARQ_API_URL}

✦ [Support](https://telegram.me/{SUPPORT_CHAT}) | ✦ [Updates](telegram.me/RajniUpdates)

╘══「 by [itzzzyashu™](t.me/Itzzzyashu) 」
"""
    await message.reply_text(
        statistics, disable_web_page_preview=True
    )


ARQ_HANDLER = CommandHandler("arq", arq)
dispatcher.add_handler(ARQ_HANDLER)
