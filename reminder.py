import pickle
from datetime import datetime
import os
from dotenv import load_dotenv
import argparse
from utils import current_time, send_message


parser = argparse.ArgumentParser()
parser.add_argument('-g', '--group', action='store_true')
args = parser.parse_args()

if args.group:
    chat_id = os.getenv('GROUP_ID')
else:
    chat_id = os.getenv('CHAT_ID')

print(current_time())

with open('/home/ilkka/Python/metrix/metrix_registered', 'rb') as cf:
    competitions = pickle.load(cf)

today = datetime.today().date()
sent = False

for c in competitions:

    if c[0] == today:

        link = 'discgolfmetrix.com/' + c[1]
        text = 'You are registered to ' + link + '\n\n' \
                + 'Remember to cancel your registration if ' \
                + 'you\'re not going to play.'

        send_message(chat_id, text)

        print('Reminder sent: ' + c[1])
        sent = True

if not sent:
    print('No reminders sent.')
