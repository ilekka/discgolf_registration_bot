#!/bin/bash

/bin/pkill -15 -f /registration_bot.py
sleep 3
/bin/bash /home/ilkka/registration_bot.sh
sleep 60
rm -f /home/ilkka/Python/metrix/restart_id
