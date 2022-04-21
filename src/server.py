from socketserver import BaseRequestHandler, ThreadingTCPServer
from threading import Thread

PORT = 8080

class TCPHandler(BaseRequestHandler):
   def handle(self):
      req = self.request
      client_name = req.getpeername()
      while True:
         data = req.recv(4096)
         msg = data.decode('utf-8')
         print(f"server receiving {msg} from {client_name}\n")


class Server(ThreadingTCPServer):
   pass

if __name__ == "__main__":
   server = Server(('localhost', PORT), TCPHandler)
   print(f"=== server serving on port {PORT} ===\n")
   Thread(target=server.serve_forever).start()