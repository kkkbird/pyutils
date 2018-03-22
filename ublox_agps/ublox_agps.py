import sys
import threading
from socket import *


USER = "lin.tang@ti-link.com.cn"
PASSWORD = "Upgfz"
SERVER = "agps.u-blox.com"
PORT = 46434

ADDR = (SERVER, PORT)

rlt = b''

def getUblox(lat, lon, pacc):
    sock = socket(AF_INET, SOCK_STREAM)  
    sock.connect(ADDR)
    
    request = ('cmd=eph;user=%s;pwd=%s;lat=%f;lon=%f;pacc=%d' % (USER, PASSWORD, lat, lon, pacc)).encode('ascii')
    sock.send(request)
    
    global rlt
    
    try:    
        while True:
            buff = sock.recv(4096)
            
            if not buff:
                break
            
            rlt += buff
    except Exception as e:
        print(e)
    
    sock.close()
    
    return rlt


if __name__ == '__main__':

    lat = 30.45
    lon = 114.17
    pacc = 1500000.0
    
    t = threading.Thread(target=getUblox, args=(lat, lon, pacc))
    t.start()
    t.join(10)
    
    #out = getUblox(lat, lon, pacc)    
    out = rlt
    
    content = out.split(b'\n', 4)
    
    if len(content) != 5:
        print('content structure error')
        sys.exit(-1)   
    
    content_length = (int)(content[1].split(b':')[1].strip())
    content_type = content[2].split(b':')[1].strip()
    
    if(content_type == 'text/plain'):
        print(content[4])
        sys.exit(-1)
        
    if(content_length != len(content[4])):
        print('content length error')
        sys.exit(-1)
        
    with open('ublox_agps.data.tmp', 'wb') as fh:
        fh.write(content[4])
        
    print('done')

