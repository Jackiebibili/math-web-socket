from queue import Queue
from socketserver import BaseRequestHandler, ThreadingTCPServer
from threading import Thread, Semaphore
from packet import Packet, PacketType
from user_msg_packet import UserMsgPacket
from user_dup_packet import UserDupPacket

DEFAULT_BUFFER_SIZE = 4096  # 4k
PORT = 8080

def configTCPHandler(buf_size=DEFAULT_BUFFER_SIZE):
   pkt_handler = Packet()
   sessions = dict()
   forward_queue = Queue()
   forward_sem = Semaphore(10)
   def message_forwarder():
      while True:
         if forward_queue.empty():
            forward_sem.acquire()
         client, socket, pkt = forward_queue.get()
         if client in sessions:
            socket.send(pkt.encode())
            # Todo: log server action


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
                     # Todo: log client action
                     sessions[client_name] = sock
                     forward_queue.put((client_name, sock, pkt))
               elif pkt.type == PacketType.USER_TERMINATE:
                  if client_name not in sessions:
                     forward_queue.put(
                         (client_name, sock, UserDupPacket('server', 'dup'.encode('utf-8'))))
                  else:
                      # Todo: log client action
                     del sessions[client_name]
                     forward_queue.put((client_name, sock, pkt))
               elif pkt.type == PacketType.USER_MESSAGE:
                  # Todo: log client action
                  # Todo: math expr evaluation
                  #ReceiveExpression = pkt.message.decode('utf-8')
                  #print(f"server receiving {ReceiveExpression} from {client_name}\n")
                  #ans = eval(ReceiveExpression)
                  ans = 0
                  result = UserMsgPacket('server', str(ans).encode('utf-8'))
                  forward_queue.put((client_name, sock, result))
               forward_sem.release()
            # print(f"server receiving {msg} from {client_name}\n")
            # server sends info back to client
            # sock.send(bytearray(msg.upper().encode()))
   return TCPHandler, message_forwarder
   


class Server(ThreadingTCPServer):
   pass

# if __name__ == "__main__":
#    server = Server(('localhost', PORT), TCPHandler)
#    print(f"=== server serving on port {PORT} ===\n")
#    Thread(target=server.serve_forever).start()