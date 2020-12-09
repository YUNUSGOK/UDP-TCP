import threading
import socket
from datetime import datetime
import json 
import time
import sys

SERVER_IP  = socket.gethostbyname(socket.gethostname())
BUFF_SIZE  = 4096

def writeToFile(data,filename):
    f = open(filename,"w")             
    f.write(data)
    f.close()  

def printTimes(recievedTimes,sendedTimes,protocol):
    dateFormat = "%m/%d/%Y, %H:%M:%S%f"
    transmissionTimes = []
    n= len(recievedTimes)
    for i in range(n):
        r = recievedTimes[i]
        s = datetime.strptime(sendedTimes[i],dateFormat)

        transmissionTimes.append((r - s).total_seconds()*1000)
    
    avgTime = sum(transmissionTimes)/len(transmissionTimes)
    startTime = datetime.strptime(sendedTimes[0],dateFormat)
    endTime =  recievedTimes[n-1]
    conTime = (endTime - startTime).total_seconds()*1000
    print(protocol,"Packets Average Transmission Time:", avgTime," ms")
    print(protocol,"Packets Total Transmission Time:", conTime," ms")

def responseMessage(id,index=-1):
    mdict = {'messageId' : id, "index" : index} 
    return json.dumps(mdict).encode('utf-8') 

 

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
        recievedTime = datetime.now()
        if not recievedMessage:
            break
        decodedMessage = json.loads(recievedMessage.decode('utf-8'))


        if  (decodedMessage["index"] == expected):
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
                recievedTime = datetime.now()
                if not recievedMessage:
                    break
                
                decodedMessage = json.loads(recievedMessage.decode('utf-8'))
                recievedFileData += decodedMessage["data"]
                recievedTimes.append(recievedTime)
                
                sendedTimes.append(decodedMessage["sendedTime"])

                conn.sendall(responseMessage(1,))

            

    writeToFile(recievedFileData,"tcp.txt") 
    printTimes(recievedTimes,sendedTimes,"TCP")
    
args = sys.argv
UDP_SERVER_PORT = int(args[1])
TDP_SERVER_PORT = int(args[2])
#udpThread = threading.Thread(target=udpServer,args=(UDP_SERVER_PORT,))
#udpThread.start()
tcpServer(TDP_SERVER_PORT)
