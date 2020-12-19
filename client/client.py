
import socket
import os
import time
from datetime import datetime
import sys
import json 
import threading
import hashlib


BUFF_SIZE = 4096 #How many bites will be readed from coming message
CLIENT_IP = socket.gethostbyname(socket.gethostname()) #Internal IP of current Host


expected = 0 #expected
changed = False # boolean value whether expected value is changed or not
lock = threading.Lock() # mutex for race condition prevention

#change value with mutex
def change(x):
    lock.acquire()
    global changed
    changed = x
    lock.release()

# Fragment file into 500 bit chunks
def fragmentFile(filename):
    f = open(filename,"r")
    i = 0 
    chunks = []
    while True:
        data = f.read(500)
        if not data:
            break
        chunks.append(data)
    return chunks
# Create message with data, sended time and 
# checksum for both UDP and TCP
def createMessage( index=0, data = ""):

    sendedTime = time.time()*1000 #current time
    header = {'sendedTime' : sendedTime,
        'index' : index, 'data': data}
    checksum = createChecksum(header) #checksum created
    message = {'header': header, "checksum": checksum }
    return json.dumps(message).encode('utf-8') #JSON to Bytes

# Every element in a json object will be hashed to create a checksum to detect errors.
# returns the sum of hash values
def createChecksum(d):
    scale = 16
    total = 0

    for i in d: 
        s = str(d[i])
        hashed = hashlib.md5(s.encode("utf-8")) 
        hexValue = hashed.hexdigest()
        total += int(hexValue,16)
    return total

def readMessage(message):
    decodedMessage = json.loads(message.decode('utf-8'))
    header = decodedMessage["header"]
    check = createChecksum(header) == decodedMessage["checksum"]
    return header,check

""" 
Reciever thread function for listening messages coming from UDP server
If server's expected value is higher than client expected change it.
"""
def reciever(UDPClientSocket,chunks):
    chunkSize = len(chunks)
    global lock
    global expected
    global changed
    count = 0
    while True:
        if not(expected<chunkSize):  # base excits chunksSize transmisson is completed
            break
        
        recievedMessage,address = UDPClientSocket.recvfrom(BUFF_SIZE)
        try:

            decodedMessage , check = readMessage(recievedMessage)
            #print("server ex:",decodedMessage["index"]," our ex:", expected)
            if(decodedMessage["index"] > expected and (check==True)):
            
                expected = decodedMessage["index"]
                change(True)
        except:
            continue

"""
Main function of UDP client which will send data to from given port to
given server IP-Port pair. 
Runs two threads: Sender thread and Receiver thread.
Sender Thread sends packets from base to windows size 100 and wait for 1 second
After 1 second it sends new windows if base is changed or just resends 
the previous ones. After transmisson is completed it will print how many packets are re-send.
Reciever thread reads incomimg messages from server and updates expected value if 
its higher than base
"""

def udpClient(SERVER_IP, SERVER_PORT_UDP, CLIENT_PORT_UDP):
    global lock 
    global changed
    global expected
    WINDOW_SIZE = 10 #How many packet will be send before wait for response
    chunks = fragmentFile("transfer_file_UDP.txt") # divide file into 500 bit chunks

    serverAddressPort = (SERVER_IP, SERVER_PORT_UDP) #Server IP-PORT pair
    clientAddressPort = (CLIENT_IP, CLIENT_PORT_UDP) #Client IP-PORT pair
    chunkSize = len(chunks) # size of the chunks which will be packet file

    #Create a UDP socket
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.bind(clientAddressPort) #bind socket to Client UDP IP-PORT pair
    recieverThread = threading.Thread(target=reciever, args=(UDPClientSocket,chunks))
    recieverThread.start() #Reciever thread begin listen incoming messages
    totalSendCount = 0 #how many packets are sended

    while True:
        base = expected # base value is what server expects
        if not(base <chunkSize): # base excits chunksSize transmisson is completed
            break
        #start sending packets from base with windows size
        for i in range(min(WINDOW_SIZE,chunkSize-base)): 
            #message with data, sended time and sended packet index
            sendedMessage = createMessage( base + i, chunks[base + i] )
            #rint(base+i)
            UDPClientSocket.sendto(sendedMessage, serverAddressPort)
            totalSendCount += 1 # increment after every packet send
        

        count = 0 #timer count
        #wait for 1 second and if expected is changed continue sending packets
        while(changed == False and count<20): 
            count += 1
            time.sleep(0.05)
        change(False) # changed to false if its true


    UDPClientSocket.sendto("".encode(), serverAddressPort) #empty message for end of the transmisson
    #Print have many packets are resended 
    print("UDP Transmission Re-transferred Packets: ", totalSendCount - chunkSize)
    #wait reciever to finish client
    recieverThread.join()

def tcpClient(SERVER_IP, SERVER_PORT_TCP, CLIENT_PORT_TCP ):
    chunks = fragmentFile("transfer_file_TCP.txt") # divide file into 500 bit chunks 
    chunkSize = len(chunks) # size of the chunks which will be packet file
    serverAddressPort = (SERVER_IP, SERVER_PORT_TCP) #Server IP-PORT pair
    clientAddressPort = (CLIENT_IP, CLIENT_PORT_TCP) #Client IP-PORT pair
    #create TCP socket
    #print(chunkSize)
    s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(clientAddressPort)#bind socket to Client TCP IP-PORT pair
    s.connect(serverAddressPort) #connect to Server TCP IP-PORT pair
    totalMessage = "".encode()

    for i in range(chunkSize): 

        # send every chunk of the file one by one
        sendedMessage = createMessage( i, chunks[i] ) #message with data, sended time and sended packet index
        n = len(sendedMessage)
        #print(n)
        padding = " "*(1000-n)
        #print(len(sendedMessage + padding.encode()))
        paddedMessage = sendedMessage + padding.encode()
        totalMessage += paddedMessage
        s.sendall(paddedMessage) # send the packet
        data = s.recv(BUFF_SIZE) # wait for ACK from server



args = sys.argv # client parameters
SERVER_IP = args[1]
SERVER_PORT_UDP = int(args[2]) # Server UDP Listener Port
SERVER_PORT_TCP = int(args[3]) # Server TCP Listener Port
CLIENT_PORT_UDP = int(args[4]) # Client UDP Sender Port
CLIENT_PORT_TCP = int(args[5]) # Client TCP Sender Port

#First TCP and then UDP will send messages to server
udpClient(SERVER_IP,SERVER_PORT_UDP, CLIENT_PORT_UDP)
tcpClient(SERVER_IP, SERVER_PORT_TCP, CLIENT_PORT_TCP)