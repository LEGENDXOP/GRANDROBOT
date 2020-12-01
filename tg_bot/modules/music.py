import html
import time
import datetime
from telegram.ext import CommandHandler, run_async, Filters
import requests, logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import Message, Chat, Update, Bot, MessageEntity
from tg_bot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from tg_bot.modules.helper_funcs.chat_status import user_admin

count = 0
@run_async
def music(bot: Bot, update: Update, args):
	message = update.effective_message
	global count

	chatId = update.message.chat_id
    
	video_id = ''.join(args)

	if video_id.find('youtu.be') != -1:
		index = video_id.rfind('/') + 1
		video_id = video_id[index:][:11]
		message.reply_text("Please wait...\ndownloading audio.")

	elif video_id.find('youtube') != -1:
		index = video_id.rfind('?v=') + 3
		video_id = video_id[index:][:11]
		message.reply_text("Please wait...\downloading audio.")

	elif not video_id.find('youtube') != -1:
		message.reply_text("Please provide me youtube link")

	elif not video_id.find('youtu.be') != -1:
		message.reply_text("Please provide me youtube link")
		

        



	r = requests.get(f'https://api.pointmp3.com/dl/{video_id}?format=mp3')
	

	json1_response = r.json()

	if not json1_response['error']:
		

		redirect_link = json1_response['url']

		r = requests.get(redirect_link)
		

		json2_response = r.json()

		if not json2_response['error']:
			payload = json2_response['payload']

			info = '*{0}* \nUploaded by @AnonymousD3061'.format(payload['fulltitle'])

			try:
				
				bot.send_audio(chat_id=chatId, audio=json2_response['url'] ,parse_mode='Markdown',text="meanya", caption=info)
				count += 1
				print("\033[1m\033[96m" + "Download count: " + str(count) + "\033[0m")
			except:
				bot.send_message(chat_id=chatId, text='Something went wrong with the download..!\nPlease Report there @AnonymousD3061')


__help__ = """ Youtube audio Downloader
 - /music <Youtube link> : download audio file from youtube link.

"""
__mod_name__ = "MP3 DOWNLOADER" 

music_handler = CommandHandler('music', music, pass_args=True)
dispatcher.add_handler(music_handler)


