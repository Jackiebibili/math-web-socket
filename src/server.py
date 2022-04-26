from socketserver import BaseRequestHandler, ThreadingTCPServer
import time

class TCPHandler(BaseRequestHandler):
   def handle(self):
      sock = self.request
      client_name = sock.getpeername()
      while True:
         # server receives info
         data = sock.recv(4096)
         msg = data.decode('utf-8')
         # print(f"server receiving {msg} from {client_name}\n")
         # server sends info back to client
         sock.send(bytearray(msg.upper().encode()))
         time.sleep(0.1)
         if not data:
            break
      sock.close()

class Server(ThreadingTCPServer):
   pass
