# coding: utf-8

import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler
import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler 
handler = logging.FileHandler('humino_bot.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


def start(bot, update):
    logger.info("Linking to {}".format(update.message.chat_id))
    update.message.reply_text("Hello.")

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def measure(bot, update):
    logger.info("Sending measurements")
    with open(os.path.join(config.OUT_FOLDER, "status.txt")) as f:
        status = f.read()

    update.message.reply_text(status)
    
    with open(os.path.join(config.OUT_FOLDER, "plot.png"), "rb") as f:
        bot.send_photo(chat_id=update.message.chat_id, photo=f)

def run():
    logger.info("Starting bot")
    args = {
        timeout = 
    }
    updater = Updater(config.TELEGRAM_API_TOKEN, request_kwargs=args)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('measure', measure))
    dp.add_error_handler(error)
    updater.start_polling()
    return updater


if __name__ == '__main__':
    updater = run()
    updater.idle()