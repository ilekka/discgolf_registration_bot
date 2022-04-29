from datetime import datetime
from telegram.ext import Updater
import os
from dotenv import load_dotenv


load_dotenv('/home/ilkka/Python/metrix/metrix.env')


def current_time():
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def send_message(chat_id, text):
    updater = Updater(token=os.getenv('TOKEN'), use_context=True)
    updater.bot.sendMessage(chat_id=chat_id, text=text)


def check(update, context):

    known_ids = [int(os.getenv('CHAT_ID')), int(os.getenv('GROUP_ID'))]

    if update.effective_chat.id in known_ids:
        return True

    else:
        text = "Go away, I don't know who you are!"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return False
