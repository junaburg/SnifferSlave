
import sys
import socket
import json
from bluepy.btle import Scanner, DefaultDelegate, Peripheral
#
class myDelegate(DefaultDelegate):
     def __init__(self):
             DefaultDelegate.__init__(self)
     def handleDiscovery(self, dev, isNewDev, isNewData):
         if isNewDev and dev.addr == "dd:33:16:00:02:dc":
                 print(f"my name is {dev.getValueText(9)}")
                 beacondict = {"address":dev.addr,"rssi":dev.rssi}
#     def handleNotification(self, cHandle, data):
#
# #Initialize Beacon
p = Peripheral("dd:33:16:00:02:dc")
p.setDelegate(myDelegate())
#
# #setup notifications
# service = p.getServicebyUUID()
# ch = service.getCharacteristics(char_uuid)[0]
# c.write(setup_data)

#
#
#
#
#
#
host = "192.168.1.12"
port = 9988
bdict = {"address": "address", "rssi":"rssi"}


def connection():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("socket created")
    s.connect((host,port))
    while True:
        try:
            command = input("Enter:")
            if command == 'kill':
                    s.send(str.encode(command))
                    break
            elif command == 'dict':
                data = str.encode(json.dumps(bdict))
                s.sendall(data)
            s.send(str.encode(command))

            print("\nAwaiting reply from: " + host)
            reply = s.recv(1024)
            print(host, " : ", reply)
            reply = reply.decode('utf-8')
            print(reply)
        except socket.error() as msg:
            print(msg)
    s.close()

connection()
