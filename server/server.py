#!/usr/bin/env python3

import socket

from datetime import datetime
import json 

BUFF_SIZE = 4096

SERVER_IP  = "10.10.1.1"  # Standard loopback interface address (localhost)
TCP_SERVER_PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
UDP_SERVER_PORT = 20001

def responseMessage(id,index=-1):
    mdict = {'messageId' : id, "index" : index} 
    return json.dumps(mdict).encode('utf-8') 

def writeToFile(data,filename):
    f = open(filename,"w")             
    f.write(data)
    f.close()  

def printTimes(recievedTimes,sendedTimes,protocol):
    transmissionTimes = []
    n= len(recievedTimes)
    for i in range(n):
        transmissionTimes.append(recievedTimes[i] - sendedTimes[i])
    
    avgTime = sum(transmissionTimes)/len(transmissionTimes)
    conTime = recievedTimes[n-1]-sendedTimes[0]
    print(protocol,"Packets Average Transmission Time:", avgTime," ms")
    print(protocol,"Packets Total Transmission Time:", conTime," ms")

def tcpServer():
    
    transmissionTimes = []
    recievedTimes = []
    sendedTimes = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        s.bind((SERVER_IP, TCP_SERVER_PORT))
        s.listen()
        conn, addr = s.accept()
        recievedFileData = ""
        connectionStartTime = datetime.now().timestamp()*1000
        with conn:
            print('Connected by', addr)
            while True:
                recievedMessage = conn.recv(BUFF_SIZE)
                recievedTime = datetime.now().timestamp()*1000
                if not recievedMessage:
                    break
                
                decodedMessage = json.loads(recievedMessage.decode('utf-8'))
                recievedFileData += decodedMessage["data"]
                recievedTimes.append(recievedTime)
                transmissionTimes.append( recievedTime-decodedMessage["sendedTime"])
                sendedTimes.append(decodedMessage["sendedTime"])
                conn.sendall(responseMessage(1,))
        connectionEndTime = datetime.now().timestamp()*1000
            

    writeToFile(recievedFileData,"transfer_file_TCP.txt.txt") 
    printTimes(recievedTimes,sendedTimes,"TCP")
    

tcpServer()
