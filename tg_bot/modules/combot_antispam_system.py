import html, time
import re
from typing import Optional, List

import tg_bot.modules.helper_funcs.cas_api as cas

from telegram import Message, Chat, Update, Bot, User, CallbackQuery, ChatMember, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity
from telegram.error import BadRequest
from tg_bot import dispatcher, OWNER_ID, DEV_USERS, SUDO_USERS, SUPPORT_USERS, TIGER_USERS, WHITELIST_USERS, LOGGER
from telegram.ext import MessageHandler, Filters, CommandHandler, run_async, CallbackQueryHandler
from telegram.utils.helpers import mention_markdown, mention_html, escape_markdown

import tg_bot.modules.sql.welcome_sql as sql
import tg_bot.modules.sql.global_bans_sql as gbansql
import tg_bot.modules.sql.users_sql as userssql

from tg_bot import dispatcher, OWNER_ID, LOGGER, SUDO_USERS, SUPPORT_USERS
from tg_bot.modules.helper_funcs.chat_status import user_admin, can_delete, is_user_ban_protected
from tg_bot.modules.helper_funcs.misc import build_keyboard, revert_buttons, send_to_list
from tg_bot.modules.helper_funcs.msg_types import get_welcome_type
from tg_bot.modules.helper_funcs.extraction import extract_user
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.filters import CustomFilters
from tg_bot.modules.helper_funcs.string_handling import markdown_parser, escape_invalid_curly_brackets
from tg_bot.modules.log_channel import loggable


@run_async
@user_admin
def setcas(bot: Bot, update: Update):
    chat = update.effective_chat
    msg = update.effective_message
    split_msg = msg.text.split(' ')
    if len(split_msg)!= 2:
        msg.reply_text("Invalid arguments!")
        return
    param = split_msg[1]
    if param == "on" or param == "true":
        sql.set_cas_status(chat.id, True)
        msg.reply_text("Successfully updated configuration.")
        return
    elif param == "off" or param == "false":
        sql.set_cas_status(chat.id, False)
        msg.reply_text("Successfully updated configuration.")
        return
    else:
        msg.reply_text("Invalid status to set!") #on or off ffs
        return

@run_async
@user_admin
def setban(bot: Bot, update: Update):
    chat = update.effective_chat
    msg = update.effective_message
    split_msg = msg.text.split(' ')
    if len(split_msg)!= 2:
        msg.reply_text("Invalid arguments!")
        return
    param = split_msg[1]
    if param == "on" or param == "true":
        sql.set_cas_autoban(chat.id, True)
        msg.reply_text("Successfully updated configuration.")
        return
    elif param == "off" or param == "false":
        sql.set_cas_autoban(chat.id, False)
        msg.reply_text("Successfully updated configuration.")
        return
    else:
        msg.reply_text("Invalid autoban definition to set!") #on or off ffs
        return

@run_async
@user_admin
def get_current_setting(bot: Bot, update: Update):
    chat = update.effective_chat
    msg = update.effective_message
    stats = sql.get_cas_status(chat.id)
    autoban = sql.get_cas_autoban(chat.id)
    rtext = "<b>CAS Preferences</b>\n\nCAS Checking: {}\nAutoban: {}".format(stats, autoban)
    msg.reply_text(rtext, parse_mode=ParseMode.HTML)
    return

@run_async
@user_admin
def getTimeSetting(bot: Bot, update: Update):
    chat = update.effective_chat
    msg = update.effective_message
    timeSetting = sql.getKickTime(chat.id)
    text = "This group will automatically kick people in " + str(timeSetting) + " seconds."
    msg.reply_text(text)
    return

@run_async
@user_admin
def setTimeSetting(bot: Bot, update: Update, args: List[str]):
    chat = update.effective_chat
    msg = update.effective_message
    if (not args) or len(args) != 1 or (not args[0].isdigit()):
        msg.reply_text("Give me a valid value to set! 30 to 900 secs")
        return
    value = int(args[0])
    if value < 30 or value > 900:
        msg.reply_text("Invalid value! Please use a value between 30 and 900 seconds (15 minutes)")
        return
    sql.setKickTime(str(chat.id), value)
    msg.reply_text("Success! Users that don't confirm being people will be kicked after " + str(value) + " seconds.")
    return

@run_async
def get_version(bot: Bot, update: Update):
    msg = update.effective_message
    ver = cas.vercheck()
    msg.reply_text("CAS API version: "+ver)
    return

@run_async
def caschecker(bot: Bot, update: Update, args: List[str]):
    #/info logic
    msg = update.effective_message  # type: Optional[Message]
    user_id = extract_user(update.effective_message, args)
    if user_id and int(user_id) != 777000:
        user = bot.get_chat(user_id)
    elif user_id and int(user_id) == 777000:
        msg.reply_text("This is Telegram. Unless you manually entered this reserved account's ID, it is likely a broadcast from a linked channel.")
        return
    elif not msg.reply_to_message and not args:
        user = msg.from_user
    elif not msg.reply_to_message and (not args or (
            len(args) >= 1 and not args[0].startswith("@") and not args[0].isdigit() and not msg.parse_entities(
        [MessageEntity.TEXT_MENTION]))):
        msg.reply_text("I can't extract a user from this.")
        return
    else:
        return

    text = "<b>CAS Check</b>:" \
           "\nID: <code>{}</code>" \
           "\nFirst Name: {}".format(user.id, html.escape(user.first_name))
    if user.last_name:
        text += "\nLast Name: {}".format(html.escape(user.last_name))
    if user.username:
        text += "\nUsername: @{}".format(html.escape(user.username))
    text += "\n\nCAS Banned: "
    result = cas.banchecker(user.id)
    text += str(result)
    if result:
        parsing = cas.offenses(user.id)
        if parsing:
            text += "\nTotal of Offenses: "
            text += str(parsing)
        parsing = cas.timeadded(user.id)
        if parsing:
            parseArray=str(parsing).split(", ")
            text += "\nDay added: "
            text += str(parseArray[1])
            text += "\nTime added: "
            text += str(parseArray[0])
            text += "\n\nAll times are in UTC"
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)



#this sends direct request to combot server. Will return true if user is banned, false if
#id invalid or user not banned
@run_async
def casquery(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message  # type: Optional[Message]
    try:
        user_id = msg.text.split(' ')[1]
    except:
        msg.reply_text("There was a problem parsing the query.")
        return
    text = "Your query returned: "
    result = cas.banchecker(user_id)
    text += str(result)
    msg.reply_text(text)        


@run_async
def gbanChat(bot: Bot, update: Update, args: List[str]):
    if args and len(args) == 1:
        chat_id = str(args[0])
        del args[0]
        try:
            banner = update.effective_user
            send_to_list(bot, SUDO_USERS,
                     "<b>Chat Blacklist</b>" \
                     "\n#BLCHAT" \
                     "\n<b>Status:</b> <code>Blacklisted</code>" \
                     "\n<b>Sudo Admin:</b> {}" \
                     "\n<b>Chat Name:</b> {}" \
                     "\n<b>ID:</b> <code>{}</code>".format(mention_html(banner.id, banner.first_name),userssql.get_chat_name(chat_id),chat_id), html=True)
            sql.blacklistChat(chat_id)
            update.effective_message.reply_text("Chat has been successfully blacklisted!")
            try:
                bot.leave_chat(int(chat_id))
            except:
                pass
        except:
            update.effective_message.reply_text("Error blacklisting chat!")
    else:
        update.effective_message.reply_text("Give me a valid chat id!") 

@run_async
def ungbanChat(bot: Bot, update: Update, args: List[str]):
    if args and len(args) == 1:
        chat_id = str(args[0])
        del args[0]
        try:
            banner = update.effective_user
            send_to_list(bot, SUDO_USERS,
                     "<b>Regression of Chat Blacklist</b>" \
                     "\n#UNBLCHAT" \
                     "\n<b>Status:</b> <code>Un-Blacklisted</code>" \
                     "\n<b>Sudo Admin:</b> {}" \
                     "\n<b>Chat Name:</b> {}" \
                     "\n<b>ID:</b> <code>{}</code>".format(mention_html(banner.id, banner.first_name),userssql.get_chat_name(chat_id),chat_id), html=True)
            sql.unblacklistChat(chat_id)
            update.effective_message.reply_text("Chat has been successfully un-blacklisted!")
        except:
            update.effective_message.reply_text("Error unblacklisting chat!")
    else:
        update.effective_message.reply_text("Give me a valid chat id!") 

@run_async
@user_admin
def setDefense(bot: Bot, update: Update, args: List[str]):
    chat = update.effective_chat
    msg = update.effective_message
    if len(args)!=1:
        msg.reply_text("Invalid arguments!")
        return
    param = args[0]
    if param == "on" or param == "true":
        sql.setDefenseStatus(chat.id, True)
        msg.reply_text("Defense mode has been turned on, this group is under attack. Every user that now joins will be auto kicked.")
        return
    elif param == "off" or param == "false":
        sql.setDefenseStatus(chat.id, False)
        msg.reply_text("Defense mode has been turned off, group is no longer under attack.")
        return
    else:
        msg.reply_text("Invalid status to set!") #on or off ffs
        return 

@run_async
@user_admin
def getDefense(bot: Bot, update: Update):
    chat = update.effective_chat
    msg = update.effective_message
    stat = sql.getDefenseStatus(chat.id)
    text = "<b>Defense Status</b>\n\nCurrently, this group has the defense setting set to: <b>{}</b>".format(stat)
    msg.reply_text(text, parse_mode=ParseMode.HTML)

# TODO: get welcome data from group butler snap
# def __import_data__(chat_id, data):
#     welcome = data.get('info', {}).get('rules')
#     welcome = welcome.replace('$username', '{username}')
#     welcome = welcome.replace('$name', '{fullname}')
#     welcome = welcome.replace('$id', '{id}')
#     welcome = welcome.replace('$title', '{chatname}')
#     welcome = welcome.replace('$surname', '{lastname}')
#     welcome = welcome.replace('$rules', '{rules}')
#     sql.set_custom_welcome(chat_id, welcome, sql.Types.TEXT)
ABOUT_CAS = "<b>Combot Anti-Spam System (CAS)</b>" \
            "\n\nCAS stands for Combot Anti-Spam, an automated system designed to detect spammers in Telegram groups."\
            "\nIf a user with any spam record connects to a CAS-secured group, the CAS system will ban that user immediately."\
            "\n\n<i>CAS bans are permanent, non-negotiable, and cannot be removed by Combot community managers.</i>" \
            "\n<i>If a CAS ban is determined to have been issued incorrectly, it will automatically be removed.</i>"

@run_async
def about_cas(bot: Bot, update: Update):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]

    if chat.type == "private":
        update.effective_message.reply_text(ABOUT_CAS, parse_mode=ParseMode.HTML)

    else:
        try:
            bot.send_message(user.id, ABOUT_CAS, parse_mode=ParseMode.HTML)

            update.effective_message.reply_text("You'll find in PM more info about CAS")
        except Unauthorized:
            update.effective_message.reply_text("Contact me in PM first to get CAS information.")


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)

def __chat_settings__(chat_id, user_id):
    welcome_pref, _, _ = sql.get_welc_pref(chat_id)
    goodbye_pref, _, _ = sql.get_gdbye_pref(chat_id)
    return "This chat has it's welcome preference set to `{}`.\n" \
           "It's goodbye preference is `{}`.".format(welcome_pref, goodbye_pref)

__help__ = """
{}
Commands:
 - /casver: Returns the API version that the bot is currently running
 - /cascheck: Checks you or another user for CAS BAN
*Admin only:*
 - /setcas <on/off/true/false>: Enables/disables CAS Checking on welcome
 - /getcas: Gets the current CAS settings
 - /setban <on/off/true/false>: Enables/disables autoban on CAS banned user detected.
 - /setdefense <on/off/true/false>: Turns on defense mode, will kick any new user automatically.
 - /getdefense: gets the current defense setting
 - /kicktime: gets the auto-kick time setting
 - /setkicktime: sets new auto-kick time value (between 30 and 900 seconds)
 - /cas: Info about CAS. (What is CAS?)
"""

__mod_name__ = "CAS"

SETCAS_HANDLER = CommandHandler("setcas", setcas, filters=Filters.group)
GETCAS_HANDLER = CommandHandler("getcas", get_current_setting, filters=Filters.group)
GETVER_HANDLER = DisableAbleCommandHandler("casver", get_version)
CASCHECK_HANDLER = CommandHandler("cascheck", caschecker, pass_args=True)
CASQUERY_HANDLER = CommandHandler("casquery", casquery, pass_args=True ,filters=CustomFilters.sudo_filter)
SETBAN_HANDLER = CommandHandler("setban", setban, filters=Filters.group)
GBANCHAT_HANDLER = CommandHandler("blchat", gbanChat, pass_args=True, filters=CustomFilters.sudo_filter)
UNGBANCHAT_HANDLER = CommandHandler("unblchat", ungbanChat, pass_args=True, filters=CustomFilters.sudo_filter)
DEFENSE_HANDLER = CommandHandler("setdefense", setDefense, pass_args=True)
GETDEF_HANDLER = CommandHandler("defense", getDefense)
GETTIMESET_HANDLER = CommandHandler("kicktime", getTimeSetting)
SETTIMER_HANDLER = CommandHandler("setkicktime", setTimeSetting, pass_args=True)
ABOUT_CAS_HANDLER = CommandHandler("cas",  about_cas)





dispatcher.add_handler(SETCAS_HANDLER)
dispatcher.add_handler(GETCAS_HANDLER)
dispatcher.add_handler(GETVER_HANDLER)
dispatcher.add_handler(CASCHECK_HANDLER)
dispatcher.add_handler(CASQUERY_HANDLER)
dispatcher.add_handler(SETBAN_HANDLER)
dispatcher.add_handler(GBANCHAT_HANDLER)
dispatcher.add_handler(UNGBANCHAT_HANDLER)
dispatcher.add_handler(DEFENSE_HANDLER)
dispatcher.add_handler(GETDEF_HANDLER)
dispatcher.add_handler(GETTIMESET_HANDLER)
dispatcher.add_handler(SETTIMER_HANDLER)
dispatcher.add_handler(ABOUT_CAS_HANDLER)




