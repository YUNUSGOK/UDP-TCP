
# Socket Programming
In this study, I learned and implemented two different file transfer method  
1. TCP 
2. UDP  (RDT - Go Back N)

I started with TCP.  TCP is connection-oriented, reliable data transfer protocol. Connection between server and client must be established before data transmission. 
UDP is connectionless unreliable data transfer protocol.   Therefore I implemented checksum to detect errors and Reliable Data Transfer method . 

## How to run

### Server
1. First run the server for listening incoming messages. Parameters will be
* UDP Server Listener Port
* TCP Server Listener Port


```bash
$ python3 server.py <udp_server_listener_port> <tcp_server_listener_port> 
$ python3 server.py 10000 11000
```
#### Optional: 
For testing UDP and RDT (Reliable Data Transfer), packet loss and delay can be added.  
* Packet corruption possibility(0-100) **(optional)**
* Delaying reordering percentage(0-100) **(optional)**
* Delay time(second) **(optional)**


```bash
$ python3 server.py <udp_server_listener_port> <tcp_server_listener_port> <packet_corruption_ratio> <delaying_ratio> <delay_time>
$ python3 server.py 10000 11000 5 20 2
```


### Client
2. Run the client for sending messages. Parameters will be 

* Server Address
* UDP Client Sender port
* TCP Client Sender port
* TCP Server Listener Port
* UDP Server Listener Port


```bash
$ python3 client.py  <server_ip> <udp_client_sender_port> <tcp_client_sender_port> <udp_server_listener_port> <tcp_server_listener_port>
python client.py 192.168.56.1 10000 11000 12000 13000
```

3. To learn server ip, you can use currentIP.py from server side.
```bash
$ python3 currentIP.py
Current location IP address is:'192.168.56.1'
```
##  Implementation
* Server start both UDP and TCP server in different threads to listen incoming messages.

* Client first start TCP client and then UDP client to send file.

#### TCP
TCP server waits for socket connection from given port . After connection established with a client , it reads messages coming from connected client and holds received times for further transmission time calculations. After that, server sends a message to client to notify message is received. After transmission is completed "transfer_file_UDP.txt" will be created from server side with transmitted data.

#### UDP
Since UDP does not establish connection with a client, it start listening to given port for messages. Server has a expected  packet that will come from client. Initially it will be zero and after every successful transmission it will be incremented.  When server receives a message, despite expected or not it will send client expected packet number.After transmission is completed “transfer_file_TCP.txt” will be created from server side with transmitted data.
Client uses **Go Back to N** for RDT and runs with two threads: Sender thread and Receiver thread.  Client start sending chunks from zero with a windows size 4. After sending 4 packages sequentially,  waits for a message from server for 1 second. If server returns a message with higher expected value from client base it will be changed to expected value and client will send next window from updated base. Receiver thread waits messages from server and checks if expected packet number of server is higher than window base or not.




#### Server Output
Client sends message with sent time. Server calculates  transmission time by subtraction received time from sent time. 

Average transmission time is the average of successful transmissions for each protocol.

Total transmission time is the time between the last message received and first message sent
```bash
TCP Packets Average Transmission Time: 0.049404296875 ms
TCP Packets Total Transmission Time: 95.959228515625  ms
UDP Packets Average Transmission Time: 43.53608447265625  ms
UDP Packets Total Transmission Time: 339341.57861328125  ms
````
#### Client Output
 Client counts every packet it sends. End of the transmission it will be subtracted  from chunk amount to calculate re-send packet amount.
```bash
UDP Transmission Re-transferred Packets:  858
```




