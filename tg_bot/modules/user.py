from tg_bot import bot, OWNER_ID
from tg_bot.data.users_db import already_user, new_user, rem_user, all_users
from telethon import events
@bot.on(events.NewMessage(incoming=True))
async def start (event):
  k = await event.get_chat()
  if already_user(k.id):
    pass
  elif not already_user(k.id):
    new_user(k.id)
    print (f"NEW GROUP ADDED ON DATABASE \nUSERNAME: {k.username}\nNAME: {k.first_name or k.title}")
  else:
    pass
@bot.on(events.NewMessage(pattern="/allchats"))
async def chats(event):
  if event.sender_id != OWNER_ID:
    return
  k = all_users()
  f = ""
  for x in k:
    try:
      X = await bot.get_entity(x)
      f += f'\nNAME: {X.first_name or X.title} USERNAME: {X.username or None}\n')
     except:
       pass
  await event.reply(str(f))
