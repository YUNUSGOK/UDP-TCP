import hashlib 
from datetime import datetime
import json

def createMessage( index=0, data = ""):

    sendedTime = datetime.now().timestamp()*1000
    header = {'sendedTime' : sendedTime,
        'index' : index, 'data': data}
    checksum = createChecksum(header)
    message = {'header': header, "checksum": checksum }
    return json.dumps(message).encode('utf-8')


def createChecksum(d):
    scale = 16
    total = 0
    print(d)
    for i in d: 
        s = str(d[i])
        hashed = hashlib.md5(s.encode("utf-8")) 
        hexValue = hashed.hexdigest()
        total += int(hexValue,16)
    return total

def readMessage(message):
    decodedMessage = json.loads(message.decode('utf-8'))
    header = decodedMessage["header"]
    header["sendedTime"] +=2 
    check = createChecksum(header) == decodedMessage["checksum"]
    return header,check

thisdict = {
  "brand": "Ford",
  "model": "Mustang",
  "year": 1964
}

print(readMessage(createMessage()))