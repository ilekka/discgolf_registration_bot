import metrix
from utils import check

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep, mktime
import random
import pickle
import os
import subprocess
import logging
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def help(update, context):

    if not check(update, context):
        return

    text = 'Disc Golf Metrix Registration Bot\n\n' \
            + 'Available commands:\n\n' \
            + '/search - Search competitions by text\n' \
            + '/register - Register by competition id\n' \
            + '/cancel - Unregister by competition id\n' \
            + '/registered - Upcoming competitions\n' \
            + '/history - All registered competitions\n' \
            + '/rating - Check current Metrix rating\n' \
            + '/logs - Send the log files\n' \
            + '/help - Show this message'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def ping(update, context):

    if not check(update, context):
        return

    context.bot.send_message(chat_id=update.effective_chat.id, text='Ping!')


def registered(update, context):

    if not check(update, context):
        return

    with open('/home/ilkka/Python/metrix/metrix_registered', 'rb') as cf:
        competitions = pickle.load(cf)

    competitions.sort(key=lambda x : x[0])

    text = 'You are registered for the following competitions:\n'

    for c in competitions:

        if c[0] >= datetime.today().date():
            d = datetime.strftime(c[0], '%d/%m/%Y')
            text = text + d + '\n' + 'discgolfmetrix.com/' + c[1] + '\n'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                             disable_web_page_preview=True)


def history(update, context):

    if not check(update, context):
        return

    with open('/home/ilkka/Python/metrix/metrix_registered', 'rb') as cf:
        competitions = pickle.load(cf)

    competitions.sort(key=lambda x : x[0], reverse=True)
    text = ''

    for c in competitions:
        d = datetime.strftime(c[0], '%d/%m/%Y')
        text = text + d + '\n' + 'discgolfmetrix.com/' + c[1] + '\n'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                             disable_web_page_preview=True)


def search(update, context):

    if not check(update, context):
        return

    search_text = update.message.text[8:]

    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)

    links_all, links_open = metrix.search(search_text, browser)

    if len(links_all) > 0:

        links_closed = list(set(links_all) - set(links_open))

        text = 'Found the following results:\n'
        for link in links_open:
            text = text + link[8:] + '\n'
        for link in links_closed:
            text = text + link[8:] + ' (*)\n'

        if len(links_closed) > 0:
            text = text + '(*) Registration not available'

    else:
        text = 'No results found.'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                             disable_web_page_preview=True)

    sleep(random.uniform(2, 4))
    browser.quit()


def register(update, context):

    if not check(update, context):
        return

    link = 'https://discgolfmetrix.com/' + update.message.text[10:]

    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)

    browser.get(link)
    sleep(random.uniform(4, 6))
    rating = metrix.login(browser)
    sleep(random.uniform(4, 6))
    result, error = metrix.register(browser, link, rating, ignore=False)
    sleep(random.uniform(6, 8))
    metrix.logout(browser)
    sleep(random.uniform(4, 6))
    browser.quit()

    if result:
        text = 'Successfully registered to ' + link[8:]
    else:
        text = 'Failed to register. (Reason: \"' + str(error).strip() + '\")'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                             disable_web_page_preview=True)


def cancel(update, context):

    if not check(update, context):
        return

    link = 'https://discgolfmetrix.com/' + update.message.text[8:]

    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)

    browser.get(link)
    sleep(random.uniform(4, 6))
    metrix.login(browser)
    sleep(random.uniform(4, 6))
    result, error = metrix.unregister(browser, link)
    sleep(random.uniform(6, 8))
    metrix.logout(browser)
    sleep(random.uniform(4, 6))
    browser.quit()

    if result:
        text = 'Successfully unregistered from ' + link[8:]
    else:
        text = 'Failed to unregister. (Reason: \"' + str(error).strip() + '\")'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                             disable_web_page_preview=True)


def rating(update, context):

    if not check(update, context):
        return

    def check_rating(update, context):

        options = Options()
        options.add_argument('--headless')
        browser = webdriver.Firefox(options=options)

        rating = metrix.login(browser)

        text = 'Your current Metrix rating is ' + str(rating)

        context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                                 disable_web_page_preview=True)

        sleep(random.uniform(10, 20))
        metrix.logout(browser)
        sleep(random.uniform(4, 6))
        browser.quit()

    def read_rating(update, context):

        with open('/home/ilkka/Python/metrix/metrix_rating', 'r') as f:
            rating = f.read()

        with open('/home/ilkka/Python/metrix/metrix_rating_date', 'r') as f:
            date = f.read()

        text = 'Your Metrix rating was ' + rating + ' when I last checked (' \
                + date + ')'

        context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                                 disable_web_page_preview=True)

    text = update.message.text[7:]

    if text == '':
        read_rating(update, context)
    else:
        check_rating(update, context)


def logs(update, context):

    if not check(update, context):
        return

    with open('/home/ilkka/metrix_log.txt', 'rb') as doc:
        context.bot.send_document(
                chat_id=update.effective_chat.id, document=doc)

    with open('/home/ilkka/bot_errors.txt', 'rb') as doc:
        context.bot.send_document(
                chat_id=update.effective_chat.id, document=doc)

    path = '/home/ilkka/metrix_syslog.txt'

    if os.path.isfile(path):
        os.remove(path)

    subprocess.call(
            ['/bin/bash', '/home/ilkka/Python/metrix/metrix_syslog.sh'])

    with open('/home/ilkka/metrix_syslog.txt', 'rb') as doc:
        context.bot.send_document(
                chat_id=update.effective_chat.id, document=doc)


def temp(update, context):

    if not check(update, context):
        return

    text = update.message.text[5:]

    if text == '':

        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read())

        text = ('T = ' + str(round(temp/1000, 1)) + ' °C')
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    else:

        with open('/home/ilkka/temperature', 'r') as data:
            temps = list(data)

        L = len(temps)
        N = int(text)

        X = []
        Y = []

        for line in temps[L-N-1:L-1]:

            T = int(line.rstrip()[-5:])
            d = datetime.strptime(line.rstrip()[:17], "%d/%m/%y %H:%M:%S")

            X.append(mktime(d.timetuple()))
            Y.append(T/1000)

        plt.figure()
        ax = plt.figure().gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        plt.plot(X, Y, '.')
        plt.xticks([])
        plt.tick_params(right=True, labelright=True)

        plt.savefig('/home/ilkka/temperature.png')
        plt.close()

        with open('/home/ilkka/temperature.png', 'rb') as doc:
            context.bot.send_document(
                    chat_id=update.effective_chat.id, document=doc)


def restart(update, context):

    if not check(update, context):
        return

    with open('/home/ilkka/Python/metrix/restart_id', 'w') as f:
        f.write(str(update.effective_chat.id))

    if update.message.text[8:] == '':
        subprocess.call(
                ['/bin/bash', '/home/ilkka/Python/metrix/stop_bot.sh'])
    else:
        subprocess.call(
                ['/bin/bash', '/home/ilkka/Python/metrix/restart_bot.sh'])


def chatid(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=str(chat_id))


def unknown(update, context):

    if not check(update, context):
        return

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")
