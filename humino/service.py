# encoding: utf-8

import bot
import arduino

if __name__ == "__main__":
    # Start telegram bot service
    updater = bot.run()

    # Start arduino service
    arduino.run()
    
    updater.idle()