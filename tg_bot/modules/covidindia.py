from telegram import ParseMode, Update, Bot, Chat
from telegram.ext import CommandHandler, MessageHandler, BaseFilter, run_async

from tg_bot import dispatcher

import requests

import json
from urllib.request import urlopen


def covindia(bot: Bot, update: Update):
    message = update.effective_message
    state = ''
    confirmed = 0
    deceased = 0
    recovered = 0
    state_input = ''.join([message.text.split(' ')[i] + ' ' for i in range(1, len(message.text.split(' ')))]).strip()
    if state_input:
        url_india = 'https://api.covid19india.org/data.json'
        json_url = urlopen(url_india)
        state_dict = json.loads(json_url.read())
        for sdict in state_dict['statewise']:
            if sdict['state'].lower() == state_input.lower():
                confirmed = sdict['confirmed']
                deceased = sdict['deaths']
                recovered = sdict['recovered']
                state = sdict['state']
                break
    
    if state:
        bot.send_message(
            message.chat.id,
            '`COVID-19 Tracker`\n*Number of confirmed cases in %s:* %s\n*Deceased:* %s\n*Recovered:* %s\n\n_Source:_ covid19india.org' % (state, confirmed, deceased, recovered),
            parse_mode = ParseMode.MARKDOWN,
            disable_web_page_preview = True
        )
    else:
        bot.send_message(
            message.chat.id,
            'You need to specify a valid Indian state!',
            parse_mode = ParseMode.MARKDOWN,
            disable_web_page_preview = True
        )

__help__ = """
 
 - /covindia <state>: Get real time COVID-19 stats for the input Indian state
"""

__mod_name__ = 'COVID-19 VIRUS'

COV_INDIA_HANDLER = CommandHandler('covindia', covindia)

dispatcher.add_handler(COV_INDIA_HANDLER)
