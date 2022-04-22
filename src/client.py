import socket
from threading import Thread
from queue import Queue

class Client():
   def __init__(self):
      # tasks = ['tasks']
      self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.client_socket.connect(('localhost', 8080))
      self.usr = "testing"
      self.q = Queue()
      # self.q.put(self.usr)

   def receive_msg(self):
      while True:
         data = self.client_socket.recv(4096)
         msg = data.decode('utf-8')
         print(f"client receiving {msg} from server\n")

   def send_msg(self):
      msg = input('enter your message: ')
      self.q.put(msg)
      while not self.q.empty():
         item = self.q.get()
         self.client_socket.send(bytearray(item.encode()))
         print(f"client sent {item} to server\n")



if __name__ == "__main__":
   client = Client()
   print("client has been created")
   Thread(target=client.send_msg).start()
   Thread(target=client.receive_msg).start()
   pass
