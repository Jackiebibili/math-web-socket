import time
from datetime import datetime
from queue import Queue
from socketserver import BaseRequestHandler, ThreadingTCPServer
from threading import Thread
from threading import Thread, Semaphore
from src.packet import Packet, PacketType
from user_msg_packet import UserMsgPacket
from user_dup_packet import UserDupPacket

log_queue = Queue()

def _log(msg):
	log_queue.put(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}')

DEFAULT_BUFFER_SIZE = 4096  # 4k
PORT = 8080

class TCPHandler(BaseRequestHandler):
   def handle(self):
      sock = self.request
      client_name = sock.getpeername()

def configTCPHandler(buf_size=DEFAULT_BUFFER_SIZE):
   pkt_handler = Packet()
   sessions = dict()
   forward_queue = Queue()
   forward_sem = Semaphore(0)

   def message_forwarder():
      while True:
         # server receives info
         data = sock.recv(4096)
         msg = data.decode('utf-8')
         _log(f'Server is receiving {msg} from {client_name}.')
         # server sends info back to client
         sock.send(bytearray(msg.upper().encode()))
         if forward_queue.empty():
            forward_sem.acquire()
         client, socket, pkt = forward_queue.get()
         if client in sessions:
            socket.send(pkt.encode())
            _log(f'Client is receiving {pkt.type} from Server.')


   class TCPHandler(BaseRequestHandler):
      def handle(self):
         sock = self.request
         start = time.time()
         client_name = sock.getpeername()
         while True:
            # server receives info
            data = sock.recv(buf_size)
            for pkt in pkt_handler.decode(data):
               if pkt.type == PacketType.USER_JOIN:
                  if client_name in sessions:
                     forward_queue.put((client_name, sock, UserDupPacket('server', 'dup'.encode('utf-8'))))
                  else:
                     _log(f'New connection from {client_name}')
                     sessions[client_name] = (sock, start)
                     forward_queue.put((client_name, sock, pkt))
               elif pkt.type == PacketType.USER_TERMINATE:
                  if client_name not in sessions:
                     forward_queue.put(
                        (client_name, sock, UserDupPacket('server', 'dup'.encode('utf-8'))))
                  else:
                     end = time.time()
                     time = (end - sessions[client_name][1])
                     period = str(datetime.timedelta(minutes=time))
                     _log(f'Terminating connection from {client_name} that lasted {period} minutes')
                     del sessions[client_name]
                     forward_queue.put((client_name, sock, pkt))
               elif pkt.type == PacketType.USER_MESSAGE:
                  _log(f'Server is receiving {ReceiveExpression} from {client_name}')
                  # Todo: math expr evaluation
                  ans = 0.0
                  result = UserMsgPacket('server', str(ans).encode('utf-8'))
                  forward_queue.put((client_name, sock, result))
               forward_sem.release()
            # print(f"server receiving {msg} from {client_name}\n")
            # server sends info back to client
            # sock.send(bytearray(msg.upper().encode()))
   return TCPHandler, message_forwarder
   


class Server(ThreadingTCPServer):
   pass

if __name__ == "__main__":
   server = Server(('localhost', PORT), TCPHandler)
   print(f"=== server serving on port {PORT} ===\n")
   Thread(target=server.serve_forever).start() 