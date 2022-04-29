from utils import current_time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from time import sleep
from datetime import datetime
import random
import argparse
import pickle
from telegram.ext import Updater
import re
import logging
import os
from dotenv import load_dotenv


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

load_dotenv('/home/ilkka/Python/metrix/metrix.env')


def search(text, browser):

    print('Searching for competitions...')

    browser.get('https://www.discgolfmetrix.com')

    competitions = browser.find_element_by_link_text('Competitions')
    sleep(random.uniform(1, 2))
    competitions.click()

    date = browser.find_element_by_id('id_filter_date')
    sleep(random.uniform(6, 8))
    date.click()
    next_days = browser.find_element_by_id('id_next')
    sleep(random.uniform(1, 2))
    next_days.send_keys(Keys.DOWN)
    sleep(random.uniform(1, 2))
    next_days.send_keys(Keys.DOWN)
    sleep(random.uniform(1, 2))
    date.click()

    search = browser.find_element_by_id('id_filter_name')
    sleep(random.uniform(3, 4))
    search.send_keys(text)
    search.send_keys(Keys.RETURN)
    alert = browser.switch_to.alert
    sleep(random.uniform(2, 3))
    alert.accept()

    sleep(random.uniform(6, 10))
    el_all = browser.find_elements_by_class_name('gridlist')
    el_open = browser.find_elements_by_partial_link_text('Registration open')

    results_all, results_open = [], []

    for elem in el_all:
        href = elem.get_attribute('href')
        if href is not None:
            print('Found link:', href)
            results_all.append(href)

    for elem in el_open:
        href = elem.get_attribute('href')
        if href is not None:
            results_open.append(href)

    return results_all, results_open


def login(browser):

    print('Logging in...')

    browser.get('https://www.discgolfmetrix.com/?u=login')

    email = browser.find_element_by_name('email')
    password = browser.find_element_by_name('password')

    sleep(random.uniform(2, 4))
    email.send_keys(os.getenv('EMAIL'))

    sleep(random.uniform(2, 4))
    password.send_keys(os.getenv('PASSWORD'))

    sleep(random.uniform(1, 2))
    password.send_keys(Keys.RETURN)

    sleep(random.uniform(4, 6))
    page = browser.find_element_by_tag_name('body')
    text = page.text

    i = text.index('METRIX RATING') - 4
    rating = int(text[i:i+3])

    with open('/home/ilkka/Python/metrix/metrix_rating', 'w') as f:
        f.write(str(rating))

    with open('/home/ilkka/Python/metrix/metrix_rating_date', 'w') as f:
        f.write(current_time())

    print('Rating =', rating)

    return rating


def register(browser, link, rating, ignore):

    def select_category(rating):

        sleep(random.uniform(2, 4))

        try:
            select = Select(browser.find_element_by_id('id_class'))

        except Exception:
            logger.exception(current_time())
            print('Did not find the menu to choose a category.')
            return

        options = select.options

        if len(options) == 1:
            print('Only one category available.')
            return

        else:

            index = None
            numbers = []

            for o in options:
                nums = [int(n) for n in re.findall(r'\b\d+\b', o.text)]
                numbers.append(nums)

            for n in numbers:

                if len(n) < 2:
                    pass

                else:
                    if min(n) < rating and max(n) >= rating:
                        index = numbers.index(n)

            if index is None:

                n_previous = 1000

                for n in numbers:
                    if len(n) > 0 and n[0] > rating and n[0] <= n_previous:
                        index = len(numbers) - numbers[::-1].index(n) - 1
                        n_previous = n[0]

            if index is None:

                print('Failed to find a good category, '
                      'choosing the one lowest down the list.')

                class_box = browser.find_element_by_id('id_class')
                sleep(random.uniform(3, 5))
                class_box.send_keys(Keys.END)

            else:

                print('Chose category: \'' + options[index].text + '\'')

                sleep(random.uniform(3, 5))
                select.select_by_index(index)

    print('Registering to ' + link[8:] + '...')

    browser.get(link)

    try:
        button = browser.find_element_by_link_text('Register here')
        sleep(random.uniform(6, 8))
        button.click()

        select_category(rating)

        button = browser.find_element_by_id('id_action_register')
        sleep(random.uniform(6, 8))
        button.click()

        if not ignore:

            comp_id = link[link.rindex('/') + 1:]

            page = browser.find_element_by_tag_name('body')
            text = page.text
            i = text.index('Date & time:') + 13

            date = text[i:i+8]
            date = datetime.strptime(date, '%m/%d/%y').date()

            comp_file = '/home/ilkka/Python/metrix/metrix_registered'

            with open(comp_file, 'rb') as cf:
                competitions = pickle.load(cf)

            competitions.append([date, comp_id])

            with open(comp_file, 'wb') as cf:
                pickle.dump(competitions, cf)

        return True, None

    except Exception as exc:
        logger.exception(current_time())
        print('Failed to register (' + link[8:] + ')')
        return False, exc


def unregister(browser, link):

    print('Unregistering from ' + link[8:] + '...')

    browser.get(link)

    try:
        button = browser.find_element_by_link_text('Edit registration...')
        sleep(random.uniform(6, 8))
        button.click()

        button = browser.find_element_by_link_text('Remove your registration')
        sleep(random.uniform(4, 6))
        button.click()

        alert = browser.switch_to.alert
        sleep(random.uniform(2, 3))
        alert.accept()

        result = True, None

    except Exception as exc:
        logger.exception(current_time())
        print('Failed to unregister.')
        result = False, exc

    if result[0]:

        reg_file = '/home/ilkka/Python/metrix/metrix_registered'

        with open(reg_file, 'rb') as cf:
            competitions = pickle.load(cf)

        comp_id = link[link.rindex('/') + 1:]

        for c in competitions:
            if c[1] == comp_id:
                competitions.remove(c)

        with open(reg_file, 'wb') as cf:
            pickle.dump(competitions, cf)

    return result


def logout(browser):

    print('Logging out...')

    menu = browser.find_element_by_link_text('Ilkka Mäkinen')
    sleep(random.uniform(4, 6))
    menu.click()

    button = browser.find_element_by_link_text('Log out')
    sleep(random.uniform(2, 4))
    button.click()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('text', type=str)
    parser.add_argument('-s', '--sleep', action='store_true')
    parser.add_argument('-v', '--visible', action='store_true')
    parser.add_argument('-m', '--message', action='store_true')
    parser.add_argument('-g', '--group', action='store_true')
    parser.add_argument('-i', '--ignore', action='store_true')
    parser.add_argument('-l', '--link', action='store_true')
    parser.add_argument('-c', '--cancel', action='store_true')
    args = parser.parse_args()

    if args.group:
        chat_id = os.getenv('CHAT_ID')
    else:
        chat_id = os.getenv('GROUP_ID')

    def registered(text):

        with open('/home/ilkka/Python/metrix/metrix_log', 'r') as f:
            read_file = f.read()

        if text in read_file:
            return True
        else:
            return False

    def main_inside_main(browser, args):

        def send_message(chat_id, text):
            updater = Updater(token=os.getenv('TOKEN'), use_context=True)
            updater.bot.sendMessage(chat_id=chat_id, text=text)

        def get_link(browser, args):

            if args.link or args.cancel:
                results = True
                link = 'https://discgolfmetrix.com/' + args.text

            else:
                sleep(random.uniform(2, 4))
                _, results = search(args.text, browser)

                if results:
                    link = results[-1]
                else:
                    link = None

            return link

        def check_registered(link):

            comp_file = '/home/ilkka/Python/metrix/metrix_registered'
            comp_id = link[link.rindex('/') + 1:]

            with open(comp_file, 'rb') as cf:
                competitions = pickle.load(cf)
                for c in competitions:
                    if c[1] == comp_id:
                        print('Already registered to ' + comp_id)
                        return True

            return False

        def register_main(browser, link, args):

            sleep(random.uniform(8, 12))
            rating = login(browser)

            sleep(random.uniform(8, 12))
            outcome, error = register(browser, link, rating, args.ignore)

            if outcome:

                if not args.ignore:

                    log_file = '/home/ilkka/Python/metrix/metrix_log'
                    with open(log_file, 'a') as reg_file:
                        reg_file.write(args.text + '\n')

                text = 'You have been registered to ' + link[8:]

            else:
                text = 'Registration failed. (' + link[8:] + ')\n' \
                        + 'Reason: \"' + str(error).strip() + '\"'

            if args.message:
                send_message(chat_id, text)

            sleep(random.uniform(8, 12))
            logout(browser)

        def unregister_main(browser, link):

            login(browser)
            sleep(random.uniform(8, 12))
            outcome, error = unregister(browser, link)

            if outcome:
                text = 'You have been unregistered from ' + link[8:]
            else:
                text = 'Failed to unregister. (' + link[8:] + ')\n' \
                        + 'Reason: \"' + str(error).strip() + '\"'

            if args.message:
                send_message(chat_id, text)

            sleep(random.uniform(8, 12))
            logout(browser)

        link = get_link(browser, args)

        if args.cancel:
            unregister_main(browser, link)
            return

        if link is None:
            print('No competitions found or registration not available.')
            return

        else:
            if args.ignore:
                reg = False
            else:
                reg = check_registered(link)

        if not reg:
            register_main(browser, link, args)

    if args.text == 'h':

        with open('/home/ilkka/Python/metrix/metrix_registered', 'rb') as cf:
            competitions = pickle.load(cf)

        competitions.sort(key=lambda x : x[0], reverse=True)

        for c in competitions:
            date = datetime.strftime(c[0], '%d/%m/%Y')
            link = 'https://discgolfmetrix.com/' + c[1]
            print(date, link)

        return

    if registered(args.text):

        print(current_time())
        print('Already registered. (' + args.text + ')')

    else:

        if args.sleep:
            sleep(random.uniform(0, 3600))

        print(current_time())

        options = Options()
        if not args.visible:
            options.add_argument('--headless')

        browser = webdriver.Firefox(options=options)

        try:
            main_inside_main(browser, args)

        except Exception:
            logger.exception(current_time())

        finally:
            sleep(random.uniform(4, 6))
            browser.quit()
            print('Browser closed.')


if __name__ == '__main__':
    main()
