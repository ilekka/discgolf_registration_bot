A script to automate registration for disc golf tournaments on [discgolfmetrix.com](https://www.discgolfmetrix.com), and a Telegram bot enabling one to interact with the script.

#### metrix.py 

Uses [Selenium](https://www.selenium.dev) to interact with the Disc Golf Metrix website and perform tasks such as registering and unregistering from competitions and checking if registration for a given competition is available.

#### registration_bot.py

A Telegram bot, based on [python-telegram-bot](https://python-telegram-bot.org/), which can be used to communicate with the registration script and issue commands to it.

#### commands.py

Definitions of the commands which can be performed by the Telegram bot.

#### reminder.py

To be run automatically each morning to check if you are signed up for a competition on that day, and to send a reminder message if that is the case.
