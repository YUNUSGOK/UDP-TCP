import threading
import socket
from datetime import datetime
import json 
import time
import sys
import random
import hashlib

SERVER_IP  = socket.gethostbyname(socket.gethostname())
BUFF_SIZE  = 4096

def writeToFile(data,filename):
    f = open(filename,"w")             
    f.write(data)
    f.close()  

def createChecksum(d):
    scale = 16
    total = 0

    for i in d: 
        s = str(d[i])
        hashed = hashlib.md5(s.encode("utf-8")) 
        hexValue = hashed.hexdigest()
        total += int(hexValue,16)
    return total

def printTimes(recievedTimes,sendedTimes,protocol):

    transmissionTimes = []
    n= len(recievedTimes)
    for i in range(n):
        r = recievedTimes[i]
        s = sendedTimes[i]

        transmissionTimes.append(r - s)
    
    avgTime = sum(transmissionTimes)/len(transmissionTimes)
    startTime = sendedTimes[0]
    endTime =  recievedTimes[n-1]
    conTime = endTime - startTime
    print(protocol,"Packets Average Transmission Time:", avgTime," ms")
    print(protocol,"Packets Total Transmission Time:", conTime," ms")

def responseMessage(id,index=-1):
    mdict = {'messageId' : id, "index" : index} 
    return json.dumps(mdict).encode('utf-8') 

def readMessage(message):
    decodedMessage = json.loads(message.decode('utf-8'))
    header = decodedMessage["header"]
    check = createChecksum(header) == decodedMessage["checksum"]
    return header,check
 

def udpServer(UDP_SERVER_PORT  =  20001):

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    
    recievedTimes = []
    sendedTimes = []
    # Bind to address and ip

    UDPServerSocket.bind((SERVER_IP, UDP_SERVER_PORT))


    # Listen for incoming datagrams
    expected = 0
    recievedFileData = ""
    while(True):

        recievedMessage, address = UDPServerSocket.recvfrom(BUFF_SIZE)
        recievedTime = time.time()*1000
        if not recievedMessage:
            break
        decodedMessage ,check = readMessage(recievedMessage)

        if  (decodedMessage["index"] == expected and check == True):
            expected += 1
            recievedTimes.append(recievedTime) 
            sendedTimes.append(decodedMessage["sendedTime"])
            UDPServerSocket.sendto(responseMessage(1,expected), address)
            recievedFileData += decodedMessage["data"]
        else:
            (UDPServerSocket.sendto(responseMessage(0, expected), address) )

    printTimes(recievedTimes,sendedTimes,"UDP")
    writeToFile(recievedFileData,"udp.txt")

def tcpServer(TCP_SERVER_PORT = 65432  ):
    
    transmissionTimes = []
    recievedTimes = []
    sendedTimes = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        s.bind((SERVER_IP, TCP_SERVER_PORT))
        s.listen()
        conn, addr = s.accept()
        recievedFileData = ""

        with conn:
            print('Connected by', addr)
            while True:

                recievedMessage = conn.recv(BUFF_SIZE)
                recievedTime = time.time()*1000
                if not recievedMessage:
                    break
                
                decodedMessage ,check = readMessage(recievedMessage)
                recievedFileData += decodedMessage["data"]
                recievedTimes.append(recievedTime)
                
                sendedTimes.append(decodedMessage["sendedTime"])

                conn.sendall(responseMessage(1,))

            

    writeToFile(recievedFileData,"tcp.txt") 
    printTimes(recievedTimes,sendedTimes,"TCP")
    
args = sys.argv
UDP_SERVER_PORT = int(args[1])
TDP_SERVER_PORT = int(args[2])
udpThread = threading.Thread(target=udpServer,args=(UDP_SERVER_PORT,))
udpThread.start()
tcpServer(TDP_SERVER_PORT)
