import os
import sys
import threading
import time
from datetime import datetime
from queue import Queue
from socketserver import BaseRequestHandler, ThreadingTCPServer
import traceback
import copy

import packet

log_queue = Queue()

def _log(msg):
	log_queue.put(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}')

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8008

sessions = dict()
packet_queue = Queue()
session_queue = Queue()

class TCPHandler(BaseRequestHandler):
	global sessions, packet_queue

	def handle(self):
		sock = self.request
		remote_host = sock.getpeername()
		_log(f'New connection from {remote_host}')
		session_queue.put((remote_host, sock))
		username = ''
		joined = False

		while True:
			try:
				raw_data = sock.recv(4096)
				if not raw_data:
					continue
				_log(f'Received {len(raw_data)} bytes from {remote_host}')
				packets = list(packet.Packet.decode(raw_data))
				for pkt in packets:
					_log(f'Received packet {pkt}')

					if joined and pkt._type != packet.PacketType.KEEPALIVE:
						packet_queue.put(pkt)

					if pkt._type == packet.PacketType.USER_JOIN:
						username = pkt.username
						_log(f'{remote_host} joined as {username}')
						joined = True
					elif pkt._type == packet.PacketType.USER_MESSAGE:
						_log(f'{username}: {pkt.message}')
					elif pkt._type == packet.PacketType.USER_DISCONNECT:
						_log(f'{remote_host} ({username}) disconnected')
						joined = False
						sock.close()
						break
			except Exception:
				_log(f'Connection from {remote_host} ({username}) closed')
				if joined and username:
					disconnect_pkt = packet.UserDisconnectPacket(packet.UserDisconnectPacket.DisconnectionReason.TIMEOUT, username)
					packet_queue.put(disconnect_pkt)
				break

class Server(ThreadingTCPServer):
	pass

def do_keep_alive():
	global sessions
	global packet_queue

	_log('Starting keep-alive thread')

	KEEP_ALIVE_INTERVAL = 0.1

	while True:
		time.sleep(KEEP_ALIVE_INTERVAL)
		pkt = packet.KeepAlivePacket()
		packet_queue.put(pkt)

def message_forwarder():
	global sessions
	global packet_queue
	global session_queue

	_log('Starting message forwarder thread')

	while True:
		pkt = packet_queue.get()
		failed_sessions = []
		
		while session_queue.qsize() > 0:
			client, sock = session_queue.get()
			if client not in sessions:
				sessions[client] = sock

		for client, session in sessions.items():
			try:
				session.send(pkt.encode())
			except Exception:
				_log(f'Failed to send packet to {client}')
				failed_sessions.append(client)
		for f in failed_sessions:
			del sessions[f]

def main():
	port = DEFAULT_PORT
	host = DEFAULT_HOST
	if len(sys.argv) > 1:
		host = int(sys.argv[1])
	if len(sys.argv) > 2:
		port = int(sys.argv[2])
	
	server = Server((host, port), TCPHandler)
	
	server_thread = threading.Thread(target=server.serve_forever)
	# server_thread.daemon = True
	server_thread.start()

	keep_alive_thread = threading.Thread(target=do_keep_alive)
	# keep_alive_thread.daemon = True
	keep_alive_thread.start()

	message_forwarder_thread = threading.Thread(target=message_forwarder)
	# message_forwarder_thread.daemon = True
	message_forwarder_thread.start()

	_log(f'Server listening on {host}:{port}')

	while True:
		while not log_queue.empty():
			line = log_queue.get()
			print(line, file=sys.stderr)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Shutting down...', file=sys.stderr)
		exit(0)
