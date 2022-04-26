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
         if data:
            num1, num2 = [int(x) for x in msg.split("+")]
            result = num1 + num2
            sock.send(bytearray(str(result).upper().encode()))
         time.sleep(0.1)

class Server(ThreadingTCPServer):
   pass
