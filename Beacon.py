import time

import requests
import os
from datetime import datetime
from logging import getLogger, config
from bluepy.btle import Scanner, DefaultDelegate, Peripheral

config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '../SnifferSlave/log.txt',
            'when': 'midnight',
            'backupCount': 60,
            'formatter': 'default',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
})

LOGGER = getLogger()

SNIFFER_SERIAL = os.getenv('SNIFFER_SERIAL')


# this handles beacon discovery and puts it into a dict
class SnifferDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.addr == "dd:33:16:00:02:dc":
            now = datetime.now()
            now_string = now.strftime("%d-%m-%Y %H:%M:%S.%fZ")
            print(f"my name is {dev.getValueText(9)}")
            if dev.getValueText(9) is not None:
                LOGGER.info("Found beacon at %s name: %s", dev.addr, dev.getValueText(9))
            else:
                LOGGER.info("no characteristics recieved")
            beacondict = {
                "sniffer_serial": SNIFFER_SERIAL,
                "address": dev.addr,
                "rssi": int(dev.rssi),
                "event_time": now_string
            }

            # send dictionary with update data here
            req = requests.put('http://192.168.4.1/api/event/',
                               headers={'content-type': 'application/json'},
                               json=beacondict
                               )
            print("sending data to host")

            # 400 is if the code sent is not a json file or not able to be sent in a json packet
            if req.status_code == 201:
                LOGGER.info("Request created successfully")
            elif req.status_code == 208:
                LOGGER.info("Duplicate request sent")
            elif req.status_code == 400:
                print("the data is incorrectly formatted or sent incorrectly")
                print(req.text)
                LOGGER.error("the data sent is formatted incorrectly")
            else:
                print("there was an error not listed")
                LOGGER.error("a status code not listed was returned")

            # There was an error processing the request

            req.close()


if __name__ == '__main__':
    # Initialize Beacon
    scanner = Scanner().withDelegate(SnifferDelegate())

    while True:
        scanner.start()
        scanner.process(10)
        scanner.stop()
        scanner.clear()
        time.sleep(1)