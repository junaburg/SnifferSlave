import socket
import json
import pdb
import time

host = '192.168.1.188'
port = 9988

def setupServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created.")
    try:
        s.bind((host, port))
    except socket.error as msg:
        print(msg)
    print("Socket bind complete.")
    return s

def setupConnection():
    s.listen(1) # Allows one connection at a time.
    conn, address = s.accept()
    print("Connected to: " + address[0] + ":" + str(address[1]))
    return conn

def dataTransfer(conn):
    while True:
        try:
            data = conn.recv(1024) # receive the data
            data = json.loads(data)
            print(data)
            reply = json.dumps(data)
            conn.send(str.encode(reply))
        except socket.error as msg:
            print(msg)
    conn.close()

s = setupServer()

while True:
    try:
        conn = setupConnection()
        dataTransfer(conn)
    except:
        break
