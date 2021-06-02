from ..data.users_db import all_users
from .. import bot
from telethon import events
@bot.on(events.NewMessage(pattern="/broadcast"))
async def br(event):
  i = 0
  I = 0
  k = all_users()
  text = event.text.split(" ", 1)[1]
  if not text:
    return await event.reply("Give msg")
  for x in k:
    try:
      await bot.send_message(x, text)
      i += 1
    except:
      I += 1
  await event.reply("DONE MSG IS BROADCASTED \n\nYOUR MSG IN NEXT LINE \n\n{}".format(text))
  print (f"SUCCESS ON BROADCASTING MSGS IN CHATS : {i-I}")
     
__mod_name__ = "Broadcasted"
__help__ = """
/broadcast msg
"""
