import socket

ip = socket.gethostbyname(socket.gethostname())
print("Current location IP address is:'"+ str(ip) +"'" )
