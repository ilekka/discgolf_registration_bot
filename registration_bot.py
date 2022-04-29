import commands
from utils import current_time

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import logging
from dotenv import load_dotenv


def main():

    load_dotenv('/home/ilkka/Python/metrix/metrix.env')

    updater = Updater(token=os.getenv('TOKEN'), use_context=True)

    dispatcher = updater.dispatcher

    for name, item in commands.__dict__.items():
        if callable(item) and item.__module__ == 'commands' \
                and name != 'unknown':
            dispatcher.add_handler(CommandHandler(name, item))

    # This should be last, so it responds only if the other handlers didn't.
    dispatcher.add_handler(MessageHandler(Filters.command, commands.unknown))

    with open('/home/ilkka/bot_errors.txt', 'w') as f:
        f.write(current_time() + '\n\n')

    if os.path.isfile('/home/ilkka/Python/metrix/restart_id'):
        with open('/home/ilkka/Python/metrix/restart_id', 'r') as f:
            chat_id = f.read()
    else:
        chat_id = os.getenv('CHAT_ID')

    updater.bot.sendMessage(chat_id=chat_id, text='Bot restarted.')

    updater.start_polling()


if __name__ == '__main__':

    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)

    try:
        main()
    except Exception:
        logger.exception(current_time())
