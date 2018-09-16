# coding: utf-8

import logging
import serial
import database

# Plant IDs in the order they are connected to the Arduino
PLANTS = [0, 1, 2, 3]

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/home/pi/humino/arduino_serial.log',
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
    ser = serial.Serial('/dev/ttyACM0', 9600)
    while True:
        yield ser.readline().decode('ascii').strip()

if __name__ == "__main__":
    try:
        for line in read_serial():
            msg = process_line(line)
            if msg:
                dt = msg[0]
                for i, plant in enumerate(PLANTS):
                    logging.info("{}: plant {} value {}".format(msg, plant, msg[i+1]))
                    database.store_measurements(plant, msg[i + 1], dt)
    except KeyboardInterrupt:
        logging.info("Closing serial monitor")
