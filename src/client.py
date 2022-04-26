import socket
from threading import Thread, Semaphore
from queue import Queue
from user_join_packet import UserJoinPacket
from user_msg_packet import UserMsgPacket
from user_terminate_packet import UserTerminatePacket
from packet import Packet, PacketType
import random
import time

DEFAULT_BUFFER_SIZE = 4096 # 4k

class Client():
   def __init__(self, username, buf_size=DEFAULT_BUFFER_SIZE):
      self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.client_socket.connect(('localhost', 8080))
      self.usr = username
      self.buf_size = buf_size
      self.q = Queue()
      self.conn_est = Semaphore(2)

   def receive_msg(self):
      pkt_handler = Packet()
      while True:
         data = self.client_socket.recv(self.buf_size)
         for pkt in pkt_handler.decode(data):
            if pkt.type == PacketType.USER_JOIN:
               # ack joining
               self.conn_est.release()
            elif pkt.type == PacketType.USER_TERMINATE:
               # ack terminating
               self.conn_est.acquire()
            elif pkt.type == PacketType.USER_MESSAGE:
               # normal packet
               result = pkt.message.decode('utf-8')
               print(f"client {self.usr} receiving {result}\n")
            elif pkt.type == PacketType.INVALID:
               # invalid packet - discard
               print("Packet received is invalid and discarded\n")

   def send_msg(self, msg):
      self.q.put(UserMsgPacket(self.usr, msg))
      while not self.q.empty():
         item = self.q.get()
         self.client_socket.send(item.encode())
         print(f"client sent {item} to server\n")
         time.sleep(random.random())
   
   def send_math_expressions(self):
       # handshaking packet
      self.q.put(UserJoinPacket(self.usr))
      self.conn_est.acquire()
      print(f"Test1")
      self.send_msg('%d+%d'%(random.randint(1, 10), random.randint(1, 10)))
      #self.send_msg('%d+%d'%(random.randint(1, 10), random.randint(1, 10)))
      #self.send_msg('%d+%d'%(random.randint(1, 10), random.randint(1, 10)))
      # closing packet
      self.q.put(UserTerminatePacket(self.usr))
