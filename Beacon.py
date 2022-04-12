import sys
import requests
import json
from datetime import datetime

from bluepy.btle import Scanner, DefaultDelegate, Peripheral


# this handles beacon discovery and puts it into a dict
class myDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev and dev.addr == "dd:33:16:00:02:dc":
            now = datetime.now()
            now_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print(f"my name is {dev.getValueText(9)}")

            self.beacondict = {
                "sniffer_serial": "xxxx-xxxx-xxxx-xxxx",
                "address": dev.addr,
                "rssi": dev.rssi,
                "source_addr": "192.168.4.7",
                "time": now_string
            }
            return True


# bdict = myDelegate().beacondict
# #setup notifications
#
#
#
#
#
#

class Data:
    def __init__(self):
        Data.__init__(self)

    def connection(self, update_data):
        # send dictionary with update data here

        req = requests.put('http://192.168.4.1/sniffer/event/',
                           headers={'content-type': 'application/json'},
                           json=update_data,
                           )
        #400 is if the code sent is not a json file or not able to be sent in a json packet
        if req.status_code == 400:
            print("the data is incorrectly formatted or sent incorrectly")
            print(req.text)
        else:
            print("there was an error or something")

        # There was an error processing the request

        req.close()


class Startup:
    # Initialize Beacon
    r = Data
    p = btle.Peripheral("dd:33:16:00:02:dc")
    while True:
        p.setDelegate(myDelegate())
        if (p):
            r.connection(myDelegate().beacondict)