# coding: utf-8

import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler
import config
import database
import humino

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

def toggle_notifications(bot, update, job_queue):
    if (len(job_queue.jobs()) == 0):
        job_queue.run_repeating(notify_about_dry_plants, 
            interval=config.STEP * 60, first=0, context=update.message.chat_id)
        logging.info("Notifications enabled for chat {}".format(update.message.chat_id))
        bot.send_message(
            chat_id=update.message.chat_id, text='Notifications enabled')
    else:
        jobs = job_queue.jobs()
        jobs[0].schedule_removal()
        logging.info("Notifications disabled")
        bot.send_message(
            chat_id=update.message.chat_id, text='Notifications disabled')

def notify_about_dry_plants(bot, job):
    logging.debug('Checking hum for notifications')
    raw = database.read_data(days=1)
    data = humino.raw_to_hum(raw)

    for plant_id in data.columns:
        if data[plant_id][-1] is None or data[plant_id][-2] is None:
            logging.warning('Missing data for {}'.format(config.PLANTS[plant_id][0]))
        else:
            dry_now = data[plant_id][-1] < config.PLANTS[plant_id][1]
            dry_before = data[plant_id][-2] < config.PLANTS[plant_id][1]
            watered_now = data[plant_id][-1] > (config.PLANTS[plant_id][1] + 5)

            if dry_now and not dry_before:
                text = "🍂 {} is thirsty now ({}%).".format(
                    config.PLANTS[plant_id][0], int(data[plant_id][-1]))
                bot.send_message(chat_id=job.context, text=text)
                logging.info("{} is dry".format(config.PLANTS[plant_id][0]))

            if dry_before and watered_now:
                text = "🌱 {} is good again ({}%).".format(
                    config.PLANTS[plant_id][0], data[plant_id][-1])
                bot.send_message(chat_id=job.context, text=text)
                logging.info("{} is not dry anymore".format(
                    config.PLANTS[plant_id][0]))

def run():
    logger.info("Starting bot")
    updater = Updater(config.TELEGRAM_API_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('measure', measure))
    dp.add_handler(CommandHandler('notify', toggle_notifications, pass_job_queue=True))
    dp.add_error_handler(error)
    updater.start_polling()
    return updater


if __name__ == '__main__':
    updater = run()
    updater.idle()