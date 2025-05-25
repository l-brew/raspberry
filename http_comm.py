import http.client
import json
import ssl
import threading
import time
from urllib.parse import urlencode, quote_plus
import traceback
import logging
from comm_layer import Comm_layer

class http_comm:
    def __init__(self,server_config ,comm:Comm_layer):
        self.sslContext = ssl.create_default_context()
        self.lock = threading.Lock()
        self.server_address=server_config.get("server_address","localhost")
        self.comm=comm

    def run(self):
        threading.Thread(target = self.fullStatus).start()
        threading.Thread(target = self.listenToServer).start()

    def update(self):
        if self.lock.locked():
            try:
                self.lock.release()
            except RuntimeError:
                print(traceback.format_exc())
                pass


    def listenToServer(self):
        while True:
            try:
                conn = http.client.HTTPSConnection(self.server_address, context=self.sslContext,timeout=10)
                conn.request("GET", "/brewserver/commands/listen/")
                r1 = conn.getresponse()
                response=r1.read()
                if response == b'':
                    continue
                form = json.loads(response.decode('utf-8'))
                logging.info("COMMAND:%s"%str(form))
                
                self.comm.command(form)

                self.comm.update()

            except :
                print(traceback.format_exc())
                time.sleep(5)
                continue
                        
    
    def fullStatus(self):
        
        while True:
            try:
                data=self.comm.get_status_dict() 
                conn = http.client.HTTPSConnection(self.server_address, context=self.sslContext)
                body=urlencode(data,quote_via=quote_plus)
                conn.request("POST", "/brewserver/status/update/",headers={"Content-Type":"application/x-www-form-urlencoded"},body=body)
                r1 = conn.getresponse()
                f=open("response.html","w")
                f.write(r1.read().decode('utf-8'))
                f.close()
            except:
                print(traceback.format_exc())
                time.sleep(5)
                continue
            self.lock.acquire()

def escape(s):
    return s


