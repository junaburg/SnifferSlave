import time
import queue
import requests
import os
import threading
from datetime import datetime
from logging import getLogger, config
import logging
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
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        }
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
})

LOGGER = getLogger()

SNIFFER_SERIAL = os.getenv('SNIFFER_SERIAL')
REQUEST_QUEUE = queue.Queue()


# this handles beacon discovery and puts it into a dict
class SnifferDelegate(DefaultDelegate):
    def __init__(self):
        super().__init__()

    def handleDiscovery(self, dev, isNewDev, isNewData):
        print(f"Discovered device {dev.addr}")
        if dev.addr == "dd:33:16:00:02:dc":
            now = datetime.now().isoformat()
            # now_string = now.strftime("%m-%d-%y %H:%M:%S.%fz")

            if dev.getValueText(9) is not None:
                # print(f"Found beacon at {dev.addr} name: {dev.getValueText(9)}")
                logging.info("Found beacon at %s name: %s", dev.addr, dev.getValueText(9))

            LOGGER.info("Request Data:\nSerial: %s\nBeacon Address: %s\nTime: %s", SNIFFER_SERIAL, dev.addr, now)
            # print(f"Request Data:\nSerial: {SNIFFER_SERIAL}\nBeacon Address: {dev.addr}\nTime: {now}")
            beacondict = {
                "sniffer_serial": SNIFFER_SERIAL,
                "beacon_addr": dev.addr,
                "rssi": int(dev.rssi),
                "event_time": now
            }

            print("Sending data to master...")

            # send dictionary with update data here
            req = requests.Request("PUT",
                                   url='http://192.168.4.1/api/event/',
                                   headers={'content-type': 'application/json'},
                                   json=beacondict
                                   )

            REQUEST_QUEUE.put(req)



class RequestHandler(threading.Thread):
    def __init__(self, q: queue.Queue[requests.Request]):
        super().__init__()
        self.req_queue = q
        self.interrupted = False

    def run(self):
        while True:
            self.process_requests()
            time.sleep(5)

    def stop(self):
        self.interrupted = True

    def process_requests(self):
        iter_count = 0
        session = requests.session()
        while iter_count < 5:
            try:
                req = self.req_queue.get(block=False)
            except queue.Empty:
                break
            else:
                # TODO: Process Request
                prepared = session.prepare_request(req)
                response = session.send(prepared)

                # 400 is if the code sent is not a json file or not able to be sent in a json packet
                if response.status_code == 201:
                    LOGGER.info("Request created successfully")
                elif response.status_code == 208:
                    LOGGER.info("Duplicate request sent")
                elif response.status_code == 400:
                    print("the data is incorrectly formatted or sent incorrectly")
                    print(response.text)
                    LOGGER.error("the data sent is formatted incorrectly")
                elif response.status_code == 500:
                    LOGGER.error("general server error or disconnect")
                else:
                    print("there was an error not listed")
                    LOGGER.error("a status code not listed was returned")
                pass
        session.close()


if __name__ == '__main__':
    # Initialize Beacon
    scanner = Scanner().withDelegate(SnifferDelegate())
    requests = RequestHandler()
    requests.start()

    while True:
        print("Scanning...")
        scanner.start()
        scanner.process(10)
        scanner.stop()
        scanner.clear()
        time.sleep(10)
