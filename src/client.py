import socket
from threading import Thread
from queue import Queue
import time
import random

class Client():

   def __init__(self, usrname: str):
      # tasks = ['tasks']
      self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.client_socket.connect(('127.0.0.1', 8080))
      self.usr = usrname
      self.count = 0
      self.q = Queue()
      Thread(target=self.send_msg).start()
      Thread(target=self.receive_msg).start()
      # self.q.put(self.usr)
      

   def receive_msg(self):
      while True:
         data = self.client_socket.recv(1024)
         msg = data.decode('utf-8')
         print(f"client {self.usr} receiving {msg} from server\n")
         self.count += 1
         if self.count >= 4:
            self.client_socket.close()
            break


   def send_msg(self):
      self.q.put('%d+%d'%(random.randint(1, 10), random.randint(1, 10)))
      self.q.put('%d+%d'%(random.randint(1, 10), random.randint(1, 10)))
      self.q.put('%d+%d'%(random.randint(1, 10), random.randint(1, 10)))
      self.q.put('%d+%d'%(random.randint(1, 10), random.randint(1, 10)))
      while not self.q.empty():
         item = self.q.get()
         print(f"client {self.usr} sent {item} to server\n")
         self.client_socket.send(bytearray(item.encode()))
         time.sleep(random.random())
      
