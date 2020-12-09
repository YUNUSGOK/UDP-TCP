
import socket
import os
import time
from datetime import datetime

import json 
import threading


BUFF_SIZE = 4096
CLIENT_IP = "127.0.0.1"
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 20001       # The port used by the server


changed = False
lock = threading.Lock()

expected = 0
stopThread = False

lock = threading.Condition(threading.Lock( ))

def change():
    lock.acquire()
    global changed
    changed = not changed
    lock.release()

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



def reciever(UDPClientSocket,chunks):
    chunkSize = len(chunks)
    global base
    global send_timer
    global lock
    global expected
    global changed
    while True:
        if not(expected<chunkSize):
            break
        
        msgFromServer,address = UDPClientSocket.recvfrom(BUFF_SIZE)
        decodedMessage = json.loads(msgFromServer.decode('utf-8'))

        if(decodedMessage["index"] > expected):
            expected = decodedMessage["index"]
            change()



def udpClient(SERVER_IP = "127.0.0.1",SERVER_PORT_UDP=20001 ,CLIENT_PORT_UDP = 49910):
    global lock
    global changed
    chunks = fragmentFile("transfer_file_UDP.txt")
    
    serverAddressPort = (SERVER_IP, SERVER_PORT_UDP)
    clientAddressPort = (CLIENT_IP, CLIENT_PORT_UDP)
    chunkSize = len(chunks)

    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.bind(clientAddressPort)
    recieverThread = threading.Thread(target=reciever, args=(UDPClientSocket,chunks))
    recieverThread.start()
    totalSendCount = 0

    while True:
        ex = expected
        if not(ex <chunkSize):
            break
        try:
            for i in range(min(4,chunkSize-ex)):
                sendedTime = (datetime.now().timestamp()*1000)
                sendedMessage = message(sendedTime, chunkSize, ex+i, chunks[ex+i])
                UDPClientSocket.sendto(sendedMessage, serverAddressPort)
                totalSendCount += 1


            count = 0
            while(changed == False and count<10):
                count += 1
                time.sleep(0.05)
            change()
        except:
            break

    UDPClientSocket.sendto("".encode(), serverAddressPort)
    print("UDP Transmission Re-transferred Packets: ",totalSendCount - chunkSize)
    stopThread = True
    recieverThread.join()

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
udpClient()