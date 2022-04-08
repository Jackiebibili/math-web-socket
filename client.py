import socket
import time
import os
import platform
import threading
import packet
import base64
import binascii
from datetime import datetime
from queue import Queue
from socketserver import BaseRequestHandler, ThreadingTCPServer
import traceback
import copy
import CaesarCipher as CC
import AESCipher as AESC
from threading import Thread
import queue


# p_user_join = packet.UserJoinPacket('deez')
# p_keepalive = packet.KeepAlivePacket()

class client():
    ''' node for sending request to server
		to iniate a communication '''

    # __________initializing a node for TCP communication___________

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8008))

    # __________ Our node server information _______________

    def __init__(self, usrname: str):
        self.usr = usrname
        self.CCenc = CC.CaesarCipher(1)
        self.AESenc = AESC.AESCipher("a;lsdkfj;")
        time.sleep(1)
        self.q = queue.Queue()
        self.q.put(packet.UserJoinPacket(self.usr))

    @property
    def receive_msg(self):
        while True:
            while self.q.empty() == False:
                self.client_socket.send(self.q.get().encode())
            data = self.client_socket.recv(4096)
            for new_msg in packet.Packet.decode(data):
                if new_msg._type == packet.PacketType.USER_MESSAGE:
                    enc_method = new_msg.encryption
                    if int(enc_method) == 0:
                        new_msg_body = self.CCenc.Decrypt(new_msg.message)
                    if int(enc_method) == 1:
                        new_msg_body = self.AESenc.Decrypt(new_msg.message)
                    if int(enc_method) == 2:
                        new_msg_body = new_msg.message.decode('utf-8')
                    print(f"\n{new_msg.username}: \n{new_msg_body}\n")
            time.sleep(0.01)

    def send_msg(self):
        while True:
            msg = input('\nPlease enter your message: ')
            encint = input('\nPlease choose a message encryption scheme: \n\tCAESAR = 0\n\tAES = 1\n\tPLAINTEXT = 2\n')
            if int(encint) == 0:
                msg = self.CCenc.Encrypt(msg)
                msg_packet = packet.UserMessagePacket(packet.UserMessagePacket.EncryptionScheme.CAESAR, self.usr, msg)
            if int(encint) == 1:
                msg = self.AESenc.Encrypt(msg)
                msg_packet = packet.UserMessagePacket(packet.UserMessagePacket.EncryptionScheme.AES, self.usr, msg)
            if int(encint) == 2:
                msg_packet = packet.UserMessagePacket(packet.UserMessagePacket.EncryptionScheme.PLAINTEXT, self.usr, msg.encode())
            self.q.put(msg_packet)
            time.sleep(0.01)


if __name__ == '__main__':
    usr = input('\nPlease enter your name: ')
    packet.UserJoinPacket(usr)
    user1 = client(usr)
    
    Thread(target=user1.send_msg).start()
    Thread(target=user1.receive_msg).start()
