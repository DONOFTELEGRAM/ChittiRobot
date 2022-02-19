import re
import os

from telethon import events, Button
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from SaitamaRobot.events import register as MEMEK
from SaitamaRobot import telethn as tbot

PHOTO = "https://telegra.ph/file/4af36e1114f010b951e98.jpg"

@MEMEK(pattern=("/mhelp"))
async def awake(event):
  tai = event.sender.first_name
  RAJNI = "** ──「 Basic Guide 」── ** \n\n"
  RAJNI += "• /play **(song title) — To Play the song you requested via YouTube** \n"
  RAJNI += "• /search ** (song/video title) – To search for links on YouTube with details** \n"
  RAJNI += "• /playlist - **show the list song in queue** \n"
  RAJNI += "•/lyric - ** (song name) lyrics scrapper** \n\n"
  RAJNI += "** ──「 Admin CMD 」── ** \n\n"
  RAJNI += "• /pause - **To Pause Song playback** \n"
  RAJNI += "• /resume - **To resume playback of the paused Song** \n"
  RAJNI += "• /skip - **To Skip playback of the song to the next Song** \n"
  RAJNI += "• /end - **To Stop Song playback** \n"
  RAJNI += "• /control - **open the player settings panel** \n"
  RAJNI += "• /reload - **To Refresh admin list** \n"

  BUTTON = [[Button.url("Support", "https://t.me/Rajnisupport"), Button.url("Updates", "https://t.me/RajniUpdates")]]
  await tbot.send_file(event.chat_id, PHOTO, caption=RAJNI,  buttons=BUTTON)
