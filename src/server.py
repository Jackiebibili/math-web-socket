from queue import Queue
from socketserver import BaseRequestHandler, ThreadingTCPServer
from threading import Semaphore, Timer
from packet import Packet, PacketType, UserMsgPacket, UserDupPacket
import time
from datetime import datetime

log_queue = Queue()
def _log(msg):
	log_queue.put(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}\n')

def _get_duration(start):
   end = round(time.time() * 1000)
   t = end - start
   return str(t) + " milliseconds"

TERMINAING_TIMEOUT = 2 # sec
DEFAULT_BUFFER_SIZE = 4096  # 4k
PORT = 8080

def configTCPHandler(buf_size=DEFAULT_BUFFER_SIZE):
   pkt_handler = Packet()
   sessions = dict()
   forward_queue = Queue()
   forward_sem = Semaphore(0)
   def message_forwarder():
      while True:
         if forward_queue.empty():
            forward_sem.acquire()
         client, socket, pkt = forward_queue.get()
         if client in sessions:
            socket.send(pkt.encode())
            # log server action
            if pkt.type == PacketType.USER_JOIN:
               _log(f"server is sending user join ack back to {client} with username {pkt.username}")
            elif pkt.type == PacketType.USER_TERMINATE:
               _log(f"server is sending user termination ack back to {client} with username {pkt.username}")
            elif pkt.type == PacketType.USER_MESSAGE:
               _log(
                   f"server is sending a message response {pkt.message.decode('utf-8')} back to {client} with username {pkt.username}")

   class TCPHandler(BaseRequestHandler):
      def handle(self):
         sock = self.request
         client_name = sock.getpeername()
         while True:
            # server receives info
            data = sock.recv(buf_size)
            for pkt in pkt_handler.decode(data):
               if pkt.type == PacketType.USER_JOIN:
                  if client_name in sessions:
                     forward_queue.put((client_name, sock, UserDupPacket('server', 'dup'.encode('utf-8'))))
                  else:
                     # log client action
                     _log(f'server is receiving join connection request from {client_name} with client username {pkt.username}')
                     sessions[client_name] = (sock, round(time.time() * 1000))
                     forward_queue.put((client_name, sock, pkt))
               elif pkt.type == PacketType.USER_TERMINATE:
                  if client_name not in sessions:
                     forward_queue.put(
                         (client_name, sock, UserDupPacket('server', 'dup'.encode('utf-8'))))
                  else:
                      # log client action
                      _log(
                          f'server is receiving termination request from {client_name} with client username {pkt.username}')
                      def lazy_termination():
                        _log(
                             f'server is terminating connection from {client_name} with client username {pkt.username} that lasted {_get_duration(sessions[client_name][1])}')
                        del sessions[client_name]
                        forward_queue.put((client_name, sock, pkt))
                      Timer(TERMINAING_TIMEOUT, lazy_termination).start()
               elif pkt.type == PacketType.USER_MESSAGE:
                  # log client action
                  receive_expression = pkt.message.decode('utf-8')
                  _log(
                      f'server is receiving {receive_expression} from {client_name} with client username {pkt.username}')
                  # Evaluate the math expression sent by the client
                  ans = eval(receive_expression)
                  result = UserMsgPacket('server', str(ans).encode('utf-8'))
                  forward_queue.put((client_name, sock, result))
               forward_sem.release()
   return TCPHandler, message_forwarder
   


class Server(ThreadingTCPServer):
   pass
