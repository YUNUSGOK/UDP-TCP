
import os
import filecmp 
dirname = os.path.dirname(__file__)
print(dirname)
tcp1 = os.path.join(dirname, 'client/transfer_file_TCP.txt')
tcp2 = os.path.join(dirname, 'server/transfer_file_TCP.txt')

udp1 = os.path.join(dirname, 'client/transfer_file_UDP.txt')
udp2 = os.path.join(dirname, 'server/transfer_file_UDP.txt')


comp1 = filecmp.cmp(tcp1 , tcp2 ) 
comp2 = filecmp.cmp(udp1 , udp2 ) 

print(comp1)
print(comp2)