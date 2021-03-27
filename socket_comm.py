import socket
import time
import sys
import pickle
import threading
import queue 

QUEUE_SIZE =1

class Socket_comm:
    def __init__(self,comm):
        self.s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.settimeout(None)
        self.queue_list=[]
        self.comm=comm


    def run(self):
        self.s.bind(('',2426))
        self.s.listen()
        while True:
            q=queue.Queue(QUEUE_SIZE)
            def conn_closed_callback(sock,a=q):
                if a in self.queue_list:
                    self.queue_list.remove(a)
                a.put(None)
                sock.close()
            conn, addr =self.s.accept()
            self.queue_list.append(q)
            try:
                q.put(self.comm.get_status_dict(),block=False)
            except:
                pass
            c=Connection(q,conn,conn_closed_callback,self.comm)
            t=threading.Thread(target=c.send_msg_task)
            t.start()
            t=threading.Thread(target=c.recv_msg_task)
            t.start()

    def update(self,msg):
        for q in self.queue_list:
            try:
                q.put(msg,block=False)
            except:
                queue.Full

class Connection:
    def __init__(self,msg_queue,socket,conn_closed_callback,comm):
        self.msg_queue=msg_queue
        self.socket=socket
        self.socket_open=True
        self.conn_closed_callback=conn_closed_callback
        self.socket_lock=threading.Lock()
        self.comm=comm

    def send_msg_task(self):
        while self.socket_open:
            msg=self.msg_queue.get()
            if msg is None:
                return
            p=Packet(msg)
            try:
                self.socket_lock.acquire()
                self.socket.settimeout(None)
                self.socket.sendall(p.get_packet())
                self.socket_lock.release()
            except BrokenPipeError:
                self.socket_open=False
                self.conn_closed_callback(self.socket)
                if self.socket_lock.locked():
                    self.socket_lock.release()

    def recv_msg_task(self):
        while self.socket_open:
            try:
                self.socket.settimeout(None)
                d= self.socket.recv(4)
                if len(d) == 0:
                    self.socket_open=False
                    self.conn_closed_callback(self.socket)
                    break
                size = int.from_bytes(d, byteorder='little', signed=False)
                self.socket.settimeout(1)
                data = self.socket.recv(size)
                if len(data) == 0:
                    self.socket_open=False
                    self.conn_closed_callback(self.socket)
                    break
                msg=pickle.loads(data)
                self.comm.command(msg)
            except ConnectionResetError:
                self.socket_open=False
                self.conn_closed_callback(self.socket)
                break

            

class Packet:
    def __init__(self,data):
        self.data = data
        self.size = sys.getsizeof(self.data)
        if self.size > 2**16 :
            raise OverflowError("Data too big")

    def get_packet_size(self):
        return self.size+4

    def get_data_size(self):
        return self.size

    def get_packet(self):
        b=pickle.dumps(self.data,protocol=4)
        return self.get_data_size().to_bytes(4,byteorder='little')+b