#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import logging
import json
from datetime import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import pandas as pd
import re

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("NTUDB Mock Attendance")
user_sheet = sheet.worksheet("Users") # User sheet
user_df = pd.DataFrame(user_sheet.get_all_records())

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)

newUser2, CONT, DATE, TIME, OVER_1830H, OVER_1830H_2, GETATT1 = range(7) # states
reason_cache, userInputName, gmail, day_cache, date_cache, time_cache = range(6) # variables

def newUser(update, context):
    user = update.message.from_user
    logger.info("1/3: User {} has created a new user via /newUser".format(user.first_name, update.message.text))
    context.bot.send_message(chat_id=update.effective_chat.id, text="👋👋 Hey there! It's just 2 steps. Firstly, please type in your Full Name 😀")
    update.message.reply_text("⌨ Please type in your *Full Name* in the chatbox: \n\n Alternatively, type /No to cancel.'⌨", parse_mode=telegram.ParseMode.MARKDOWN)
    return newUser2

def newUser2(update, context):
    user = update.message.from_user
    logger.info("2/3: User {} has entered Full Name {} to create user".format(user.first_name, update.message.text))
    context.bot.send_message(chat_id=update.effective_chat.id, text="🙏 Thanks, one final step 🙏", parse_mode=telegram.ParseMode.MARKDOWN)
    global userInputName
    userInputName = update.message.text
    update.message.reply_text("⌨ Please type in your *gmail* so that the spreadsheet can be shared to you: \n\n Alternatively, type /No to cancel.'⌨", parse_mode=telegram.ParseMode.MARKDOWN)
    return newUser3
    
def newUser3(update, context):
    user = update.message.from_user
    logger.info("3/3: User {} has entered gmail {} to create user".format(user.first_name, update.message.text))
    global gmail
    gmail = update.message.text
    sheet.share(gmail, perm_type='user', role='reader')
    context.bot.send_message(chat_id=update.effective_chat.id, text="🙏 Thanks 🙏 \n\n Your Telegram user *{}* will be associated with name *{}*. \n\n Gsheets has also been shared to *{}* 👍.".format(user.first_name, userInputName, gmail), parse_mode=telegram.ParseMode.MARKDOWN)
    user_sheet = sheet.worksheet("Users")
    array = [user.id, user.first_name, user.last_name, user.full_name, user.username, userInputName, gmail]
    df = pd.DataFrame(user_sheet.get_all_records())
    df.loc[len(df)] = array
    user_sheet.update([df.columns.values.tolist()] + df.values.tolist())
    return ConversationHandler.END  

def getUser(update, context):
    user = update.message.from_user
    logger.info("User {} queried for all users".format(user.first_name, update.message.text))
    context.bot.send_message(chat_id=update.effective_chat.id, text="😉 Here you go:".format(user.first_name, update.message.text), parse_mode=telegram.ParseMode.MARKDOWN)
    user_sheet = sheet.worksheet("Users")
    df = pd.DataFrame(user_sheet.get_all_records())
    df = df[["firstName", "userInputName"]]
    context.bot.send_message(chat_id=update.effective_chat.id, text=df.to_string())

def start(update, context):
    user = update.message.from_user
    logger.info("1: User {} started giving attendance via /start".format(user.first_name))
    context.bot.send_message(chat_id=update.effective_chat.id, text="👋 Hello, I'm an NTUDB attendance bot! 😀")
    kb = [[telegram.KeyboardButton('/Yes')],
          [telegram.KeyboardButton('/No')]]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True)
    update.message.reply_text("🚀  Are you ready to commit your attendance 🔥", reply_markup=kb_markup)
    return CONT

def cont_to_date(update, context):
    user = update.message.from_user
    logger.info("2: User {} confirmed giving attendance via /Yes".format(user.first_name, update.message.text))
    context.bot.send_message(chat_id=update.effective_chat.id, text="😮 Wow that's some enthusiasm there! 😮")
    TODAY = datetime.today().strftime("%A, %Y/%m/%d")
    context.bot.send_message(chat_id=update.effective_chat.id, text="📅 Today is *{}*.".format(TODAY), parse_mode=telegram.ParseMode.MARKDOWN)
    # context.bot.send_message(chat_id=update.effective_chat.id, text="Which is also time for you to wAkE tHE fK UP 😥😥 \n\njkjk 🥰.".format(TODAY), parse_mode=telegram.ParseMode.MARKDOWN)
    THIS_YEAR = datetime.today().isocalendar()[0]
    THIS_WEEK = datetime.today().isocalendar()[1]
    if datetime.today().isocalendar()[2] < 4:
        context.bot.send_message(chat_id=update.effective_chat.id, text="jkjk 🥰.\n\n Since it's still *NOT Thurs*, you can select for this week's attendance.", parse_mode=telegram.ParseMode.MARKDOWN)
        kb = [[telegram.KeyboardButton(datetime.fromisocalendar(THIS_YEAR, THIS_WEEK, 1).strftime("%a, %Y/%m/%d"))],
              [telegram.KeyboardButton(datetime.fromisocalendar(THIS_YEAR, THIS_WEEK, 3).strftime("%a, %Y/%m/%d"))]]
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Since it's *PAST Thurs*, you can indicate for next week's attendance.", parse_mode=telegram.ParseMode.MARKDOWN)
        kb = [[telegram.KeyboardButton(datetime.fromisocalendar(THIS_YEAR, THIS_WEEK+1, 1).strftime("%a, %Y/%m/%d"))],
              [telegram.KeyboardButton(datetime.fromisocalendar(THIS_YEAR, THIS_WEEK+1, 3).strftime("%a, %Y/%m/%d"))]]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True)
    update.message.reply_text("✅ Indicate the date you would come for: \n\n Alternatively, you can type in the format 'Day, 'yyyy/mm/dd'", reply_markup=kb_markup, parse_mode=telegram.ParseMode.MARKDOWN)
    return TIME

def date_to_time(update, context):
    user = update.message.from_user
    logger.info("3: User {} has selected date {} for attendance".format(user.first_name, update.message.text))
    user = update.message.from_user
    global day_cache, date_cache
    day_cache = datetime.strptime(update.message.text, "%a, %Y/%m/%d").strftime("%A")
    date_cache = datetime.strptime(update.message.text, "%a, %Y/%m/%d").strftime("%Y/%m/%d")
    userInputName = user_df[user_df["id"]==user.id]["userInputName"].values[0]
    context.bot.send_message(chat_id=update.effective_chat.id, text="🙏 Very well *{}*, Selected: \n\n *{}*".format(userInputName, update.message.text), parse_mode=telegram.ParseMode.MARKDOWN)
    context.bot.send_message(chat_id=update.effective_chat.id, text="🏆 One more option left 🏆")
    kb = [[telegram.KeyboardButton("🕔 1730H")],
          [telegram.KeyboardButton("🕕 1830H onwards")]]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True)
    update.message.reply_text("✅ Indicate the time you would come for:", reply_markup=kb_markup)
    return OVER_1830H

def time1730H_to_end(update, context):
    user = update.message.from_user
    logger.info("4: User {} has selected time {} for attendance".format(user.first_name, update.message.text))
    global time_cache
    time_cache = re.findall(r"(1730)H$", update.message.text)[0]
    logger.info("User {} has selected {}".format(user.first_name, update.message.text))
    userInputName = user_df[user_df["id"]==user.id]["userInputName"].values[0]
    attn_sheet = sheet.worksheet("Attendance")
    timestampNow = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    array = [timestampNow, user.id, user.username, user.full_name, userInputName, day_cache, date_cache, time_cache, reason_cache]
    df = pd.DataFrame(attn_sheet.get_all_records())
    df.loc[len(df)] = array
    attn_sheet.update([df.columns.values.tolist()] + df.values.tolist())
    context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Voila {}! You're all set. See you on {} 🙏".format(userInputName, update.message.text), parse_mode=telegram.ParseMode.MARKDOWN)
    return ConversationHandler.END

def over_1830H(update, context):
    user = update.message.from_user
    logger.info("4: User {} has selected time {} for attendance".format(user.first_name, update.message.text))
    context.bot.send_message(chat_id=update.effective_chat.id, text="✍ Please write down ETA separated by reason: ")
    context.bot.send_message(chat_id=update.effective_chat.id, text="*Format:* e.g.: 1845 urgent project meeting", parse_mode=telegram.ParseMode.MARKDOWN)
    return OVER_1830H_2
    
def over_1830H_2(update, context):
    user = update.message.from_user
    logger.info("5: User {} has given reason {} for attendance".format(user.first_name, update.message.text))
    global time_cache, reason_cache
    time_cache = update.message.text.split(" ")[0]
    reason_cache = " ".join(update.message.text.split(" ")[1:])
    userInputName = user_df[user_df["id"]==user.id]["userInputName"].values[0]
    attn_sheet = sheet.worksheet("Attendance")
    timestampNow = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    array = [timestampNow, user.id, user.username, user.full_name, userInputName, day_cache, date_cache, time_cache, reason_cache]
    df = pd.DataFrame(attn_sheet.get_all_records())
    df.loc[len(df)] = array
    attn_sheet.update([df.columns.values.tolist()] + df.values.tolist())
    context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Voila! You're all set. You have indicated *{}H* because of *'{}'*".format(time_cache, reason_cache), parse_mode=telegram.ParseMode.MARKDOWN)
    return ConversationHandler.END

def getAttendance(update, context):
    user = update.message.from_user
    logger.info("1/2: User {} has started querying for attendance".format(user.first_name, update.message.text))
    context.bot.send_message(chat_id=update.effective_chat.id, text="👇 Please select the date of attendance 👇")
    TODAY = datetime.today().strftime("%A, %Y/%m/%d")
    context.bot.send_message(chat_id=update.effective_chat.id, text="📅 Today is *{}*.".format(TODAY), parse_mode=telegram.ParseMode.MARKDOWN)
    # context.bot.send_message(chat_id=update.effective_chat.id, text="Which is also time for you to wAkE tHE fK UP 😥😥 \n\njkjk 🥰.".format(TODAY), parse_mode=telegram.ParseMode.MARKDOWN)
    THIS_YEAR = datetime.today().isocalendar()[0]
    THIS_WEEK = datetime.today().isocalendar()[1]
    if datetime.today().isocalendar()[2] < 4:
        context.bot.send_message(chat_id=update.effective_chat.id, text="jkjk 🥰.\n\n Since it's still *NOT Thurs*, I've prepared options for this week's attendance.", parse_mode=telegram.ParseMode.MARKDOWN)
        kb = [[telegram.KeyboardButton(datetime.fromisocalendar(THIS_YEAR, THIS_WEEK, 1).strftime("%Y/%m/%d"))],
              [telegram.KeyboardButton(datetime.fromisocalendar(THIS_YEAR, THIS_WEEK, 3).strftime("%Y/%m/%d"))]]
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Since it's *PAST Thurs*, I've prepared options for next week's attendance.", parse_mode=telegram.ParseMode.MARKDOWN)
        kb = [[telegram.KeyboardButton(datetime.fromisocalendar(THIS_YEAR, THIS_WEEK+1, 1).strftime("%Y/%m/%d"))],
              [telegram.KeyboardButton(datetime.fromisocalendar(THIS_YEAR, THIS_WEEK+1, 3).strftime("%Y/%m/%d"))]]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True)
    update.message.reply_text("✅ Indicate the date you would come for: \n\n Alternatively, you can type in the format 'yyyy/mm/dd' or type /No to cancel.", reply_markup=kb_markup, parse_mode=telegram.ParseMode.MARKDOWN)
    return GETATT1

def getAttendance1(update, context):
    user = update.message.from_user
    logger.info("2/2: User {} has continued querying for attendance on {}.".format(user.first_name, update.message.text))
    date_request = update.message.text
    attn_sheet = sheet.worksheet("Attendance")
    df = pd.DataFrame(attn_sheet.get_all_records())
    df = df[df["trainingDate"] == date_request][["userInputName", "trainingDate", "trainingTime", "reason"]]
    context.bot.send_message(chat_id=update.effective_chat.id, text=df.to_string())
    context.bot.send_message(chat_id=update.effective_chat.id, text="😌 That's all! Thanks for using me. 😌")
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation via /No.", user.first_name)
    update.message.reply_text('Bye! Hope we can talk again soon. You know where to (/start) 😁',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def help(update, context):
    user = update.message.from_user
    logger.info("User %s queried for commands via /help", user.first_name)
    context.bot.send_message(chat_id=update.effective_chat.id, text="😃 Calm down, it's not rocket science. 😃")
    context.bot.send_message(chat_id=update.effective_chat.id, text='''
Commands:
/newUser - Register yourself
/getUsers - Get registered users
/start - Give attendance
/getAtt - Get attendance
/help - This again lol''')

def main():
    f = open("NTUDB_Bot_API.txt")
    TOKEN = f.readlines()[0]
    f.close()
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Give Attendance
    attn_conv_handler = ConversationHandler(
        entry_points = [CommandHandler('start', start)],
        states={
            CONT: [CommandHandler('Yes', cont_to_date), CommandHandler('No', cancel)],
            TIME: [MessageHandler(Filters.regex('^(Mon|Tue|Wed|Thu|Fri|Sat|Sun), (\d{4})\/(0?[1-9]|1[012])\/(0?[1-9]|[12][0-9]|3[01])'), date_to_time)],
            OVER_1830H: [MessageHandler(Filters.regex('onwards$'), over_1830H),
                        MessageHandler(Filters.regex('1730H$'), time1730H_to_end)],
            OVER_1830H_2: [MessageHandler(Filters.text, over_1830H_2)]
        },
        fallbacks=[CommandHandler('No', cancel)])
    dispatcher.add_handler(attn_conv_handler)
    
    # Get Attendance
    getAtt = CommandHandler('getAtt', getAttendance)
    give_attn_conv_handler = ConversationHandler(
        entry_points = [CommandHandler('getAtt', getAttendance)],
        states={
            GETATT1: [MessageHandler(Filters.text, getAttendance1)]
        },
        fallbacks=[CommandHandler('No', cancel)])
    dispatcher.add_handler(give_attn_conv_handler)
  
    # Users 
    user_conv_handler = ConversationHandler(
        entry_points = [CommandHandler('newUser', newUser)],
        states={
            newUser2: [MessageHandler(Filters.text, newUser2), CommandHandler('No', cancel)],
            newUser3: [MessageHandler(Filters.regex('(.*)@gmail.com$'), newUser3), CommandHandler('No', cancel)]
        },
        fallbacks=[CommandHandler('No', cancel)])
    dispatcher.add_handler(user_conv_handler)
    getUsers = CommandHandler('getUsers', getUser)
    dispatcher.add_handler(getUsers)

    # Help
    helpCommand = CommandHandler('help', help)
    dispatcher.add_handler(helpCommand)

    # Launch
    updater.start_polling() # Start locally hosting Bot
    updater.idle()  # Run the bot until you press Ctrl-C or the process receives SIGINT,

    # PORT = int(os.environ.get('PORT', 5000))
    # updater.start_webhook(listen="0.0.0.0",
                          # port=int(PORT),
                          # url_path=TOKEN)
    # updater.bot.setWebhook('https://my-stoic-telebot.herokuapp.com/' + TOKEN)
    
if __name__ == '__main__':
    main()