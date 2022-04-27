import socket
from threading import Semaphore
from queue import Queue
from packet import Packet, PacketType, UserJoinPacket, UserMsgPacket, UserTerminatePacket

DEFAULT_BUFFER_SIZE = 4096 # 4k
PORT = 8080
class Client():
   def __init__(self, username, buf_size=DEFAULT_BUFFER_SIZE):
      self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.client_socket.connect(('localhost', PORT))
      self.usr = username
      self.buf_size = buf_size
      self.q = Queue()
      self.conn_est = Semaphore(0)

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
            elif pkt.type == PacketType.INVALID:
               # invalid packet - discard
               print("packet received is invalid and discarded\n")

   def send_msg(self, msg):
      self.q.put(UserMsgPacket(self.usr, msg.encode('utf-8')))
      while not self.q.empty():
         item = self.q.get()
         self.client_socket.send(item.encode())

   def send_pkt(self, pkt):
      self.q.put(pkt)
      while not self.q.empty():
         item = self.q.get()
         self.client_socket.send(item.encode())

   def send_math_expressions(self, arr):
       # handshaking packet
      self.send_pkt(UserJoinPacket(self.usr))
      self.conn_est.acquire()
      for msg in arr: # receives expressions as an array
         self.send_msg(msg)
      # closing packet
      self.send_pkt(UserTerminatePacket(self.usr))
