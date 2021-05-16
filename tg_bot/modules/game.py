"""
MADE BY LEGENDX22 🔥
THIS IS ADULT GAME BOT
BUT THIS IS NOW NOT READY
PLEASE WAIT WE ADDED YOU ON DATABSE
WHEN THIS GAME IS COMPLETED I WILL SEND YOU A MESSAGE
IF YOU WANT NOT PLAY THIS GAME THEN TYPE `/terminate`
OK BRO BYE 🤠🤠🤠
"""
from telethon import events
from tg_bot import bot, OWNER_ID as ui
from tg_bot.data.users_db import new_user, already_user, rem_user, all_users
@bot.on(events.NewMessage(pattern="/register"))
async def pro(event):
  if already_user(event.sender_id):
    await event.reply("YOU ARE ALREADY REGISTERD")
  elif not already_user(event.sender_id):
    new_user(event.sender_id)
    await event.reply(__doc__)
  else:
   pass
@bot.on(events.NewMessage(pattern="/terminate"))
async def terminate (event):
  if not already_user(event.senderer_id)
    await event.reply("YOU ARE NOT IN THE GAME USE /register FOR REGISTERING")
  elif already_user(event.sender_id):
    rem_user(event.sender_id)
    await event.reply("DONE WE REMOVED YOU, NOW YOU NOT IN GAME")
  else:
    pass
@bot.on(events.NewMessage(pattern='/allusers'))
async def all(event):
  if event.sender_id == ui:
    k = all_users()
    await event.reply(k)
