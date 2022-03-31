import socket
import json
import pdb
import time

host = '192.168.1.12'
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
            data = data.decode('utf-8')
            if data == 'kill':
                print("Server is shutting down.")
                s.close()
                break
            elif data == 'test':
                reply = "1"
            elif data == 'dict':
                reply = str.encode(json.dumps(data))
            else:
                reply = 'Unknown Command'
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
