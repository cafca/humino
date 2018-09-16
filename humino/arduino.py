# coding: utf-8

import os
import logging
import serial
import database
import config

# Plant IDs in the order they are connected to the Arduino


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=os.path.join(config.OUT_FOLDER, 'arduino_serial.log'),
                    filemode='w')

def process_line(line):
    # Read a line received via serial and yield measurements as list
    rv = None
    # import pdb;pdb.set_trace()
    kind = line[:line.index(" ")]
    msg = line[line.index(" ") + 1:]

    if kind == "status":
        logging.debug("Arduino: {}".format(msg))
    elif kind == "measurement":
        logging.debug("Measured {}".format(msg))
        rv = msg.split(",")
    return rv

def read_serial():
    logging.info("Connecting to Arduino...")
    ser = serial.Serial(config.SERIAL_DEVICE, 9600)
    while True:
        yield ser.readline().decode('ascii').strip()


def run():
    try:
        for line in read_serial():
            msg = process_line(line)
            if msg:
                dt = msg[0]
                for i, plant in enumerate(config.PLANTS):
                    logging.info("{}: plant {} value {}".format(msg, plant, msg[i+1]))
                    database.store_measurements(plant, msg[i + 1], dt)
    except KeyboardInterrupt:
        logging.info("Closing serial monitor")


if __name__ == "__main__":
    run()