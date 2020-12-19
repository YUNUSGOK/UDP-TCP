import threading
import socket
from datetime import datetime
import json 
import time
import sys
import random
import hashlib


SERVER_IP  = socket.gethostbyname(socket.gethostname()) #Internal IP of current Host

BUFF_SIZE  = 1000 #How many bites will be readed from coming message

#Method to write given data to given filename
def writeToFile(data,filename):
    f = open(filename,"w")             
    f.write(data)
    f.close()  

# Every element in a json object will be hashed to create a checksum to detect errors.
# returns the sum of hash values
def createChecksum(d):
    scale = 16
    total = 0

    for i in d: 
        s = str(d[i]) # For non-stiring values like sendedTime or index
        hashed = hashlib.md5(s.encode("utf-8")) 
        hexValue = hashed.hexdigest()
        total += int(hexValue,16)
    return total

def decision(p):
    return random.random() < p

"""
Output of the server for each protocol.
Calculates transmisson times by subsraction recievedTime from sendedTime.
Total transmisson time is the substration of Last recieved time from first sendedTime
"""
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

#Server response message includes expected index of UDP server
def responseMessage(id,index=-1):
    header = {'messageId' : id, "index" : index}
    checksum = createChecksum(header)
    message = {'header': header, "checksum": checksum }
    return json.dumps(message).encode('utf-8') #JSON to Bytes

"""
Message came from client contains a checksum and message itself
This method reads seperates checksum and message to header and checksum
"""
def readMessage(message):
    decodedMessage = json.loads(message.decode('utf-8'))
    header = decodedMessage["header"]
    check = createChecksum(header) == decodedMessage["checksum"]
    return header,check
 

"""
Main method of UDP Server that will listen given UDP_SERVER_PORT.
Reads messages coming client, checks bit error and if packet number of recieved packet is the expected, 
expected number will be incremented.
Sends the expected packet number to the client.
After transmisson is completed  printTimes() method will be called and 
recieved data will be written to "transfer_file_UDP.txt"
Packet corrpution and delay will occur with given parameters
"""
def udpServer(UDP_SERVER_PORT , packet_corruption_ratio = 0, delaying_ratio = 0 , delay_time = 0 ):

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) #Creating a UDP socket

    
    recievedTimes = [] # Message recieve times array
    sendedTimes = [] # Message send times array


    UDPServerSocket.bind((SERVER_IP, UDP_SERVER_PORT))    # Bind socket to address and ip

    expected = 0 # Expected file number(intially zero)
    recievedFileData = "" #readed file data

    while(True): #Read incoming messages until transmisson is complited

        recievedMessage, address = UDPServerSocket.recvfrom(BUFF_SIZE) # incoming message and client address
        recievedTime = time.time()*1000 # recieve time of the message
        if not recievedMessage: # If an empty message is sended and the transmisson
            break
        try:
            decodedMessage , check = readMessage(recievedMessage) #Byte to JSON message and bit error check
            if(decision(packet_corruption_ratio/100)): #Packet loss will occur with given probability
                continue
            print("recieved",decodedMessage["index"],"expected",expected)
            if  (decodedMessage["index"] == expected and check == True): #no bit error and expected packet arrived
                if(decision(delaying_ratio/100)): # delay will occur with given probablity
                    time.sleep(delay_time)
                expected += 1 # expected packet number will be inceremented 
                sendedTimes.append(decodedMessage["sendedTime"]) # sended time will be saved for further calculations
                recievedTimes.append(recievedTime)  # recieved time will be saved for further calculations
                UDPServerSocket.sendto(responseMessage(1,expected), address) #ACK will be sended
                recievedFileData += decodedMessage["data"]  # recieved data will be saved
            else:
                (UDPServerSocket.sendto(responseMessage(0, expected), address) ) #ACK will be sended
        except:
            continue

    printTimes(recievedTimes,sendedTimes,"UDP") # print avg and total time
    writeToFile(recievedFileData,"transfer_file_UDP.txt") #writes given data to 

"""
Main method of TCP Server that will listen and  accept clients given TCP_SERVER_PORT.
Reads messages coming client and send ACK to client
After transmisson is completed  printTimes() method will be called to print avg and total times 
and recieved data will be written to "transfer_file_TCP.txt"
"""
def tcpServer(TCP_SERVER_PORT ):
    
    recievedTimes = [] # Message recieve times array
    sendedTimes = [] # Message send times array

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # opens a TCP socket
        
        s.bind((SERVER_IP, TCP_SERVER_PORT))    # Bind socket to address and ip
        s.listen() # wait for a client to connect
        conn, addr = s.accept() #accept connection
        recievedFileData = ""    #readed file data
        #print(addr)
        with conn: # opens the connection for the client

            while True: #waits and reads message coming from client

                recievedMessage = conn.recv(BUFF_SIZE)  # incoming message
                recievedTime = time.time()*1000 # recieve time of the message
                if not recievedMessage: # transmisson is completed
                    break
                #print(len(recievedMessage))

                decodedMessage ,_  = readMessage(recievedMessage) #Byte to JSON message

                #print(decodedMessage)
                recievedFileData += decodedMessage["data"] # recieved data will be saved
                recievedTimes.append(recievedTime) # recieved time will be saved
                
                sendedTimes.append(decodedMessage["sendedTime"]) # sended data will be saved

                #conn.sendall(responseMessage(1,)) #ACK will be sended
            s.shutdown(1)

            

    printTimes(recievedTimes,sendedTimes,"TCP") # print avg and total time
    writeToFile(recievedFileData,"transfer_file_TCP.txt") #writes given data to 
    
args = sys.argv # server parameters
UDP_SERVER_PORT = int(args[1]) # Server UDP Listener Port
TDP_SERVER_PORT = int(args[2]) # Server TCP Listener Port
try: #Server options block for packet delay and loss
    packet_corruption_ratio = int(args[3])
    delaying_ratio = int(args[4])
    delay_time = float(args[5])
    udpThread = threading.Thread(target=udpServer,args=(UDP_SERVER_PORT,packet_corruption_ratio,delaying_ratio, delay_time))
except:
    udpThread = threading.Thread(target=udpServer,args=(UDP_SERVER_PORT,))

udpThread.start() #UDP server Thread
tcpServer(TDP_SERVER_PORT) #TCP server Thread
