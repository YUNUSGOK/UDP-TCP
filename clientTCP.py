#!/usr/bin/env python3

import socket
import os
import time
from datetime import datetime
import json 

BUFF_SIZE = 4096
CLIENT_IP = "127.0.0.1"

def fragmentFile(filename):
    f = open(filename,"r")
    i = 0 
    chunks = []
    while True:
        data = f.read(1000)
        if not data:
            break
        chunks.append(data)
    return chunks


def message(sendedTime, chunkSize=0, index=0, data = ""):
    mdict = {'sendedTime' : sendedTime,
        "chunksize": chunkSize,'index' : index, 'data': data} 
    return json.dumps(mdict).encode('utf-8') 

def tcpClient(SERVER_IP = "127.0.0.1",SERVER_PORT_TCP =65432 , CLIENT_PORT_TCP = 49911):
    chunks = fragmentFile("transfer_file_TCP.txt")
    chunkSize = len(chunks)
    serverAddressPort = (SERVER_IP, SERVER_PORT_TCP)
    clientAddressPort = (CLIENT_IP, CLIENT_PORT_TCP)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(clientAddressPort)
        s.connect(serverAddressPort)
        
        for i in range(chunkSize):

            sendedTime = (datetime.now().timestamp()*1000)
            
            sendedMessage = message(sendedTime, chunkSize, i, chunks[i] )
            s.sendall(sendedMessage)
            data = s.recv(BUFF_SIZE)



tcpClient()