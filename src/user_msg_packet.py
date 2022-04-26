from packet import Packet, PacketType
import struct


class UserMsgPacket(Packet):
   def __init__(self, username, msg):
      self.type = PacketType.USER_MESSAGE
      self.format = '<HH'
      self.username = username
      self.message = msg

   def _encode_data(self):
      usr_length = len(self.username)
      msg_length = len(self.message)
      packet_format = f'{self.format}{str(usr_length)}s{str(msg_length)}s'
      return struct.pack(packet_format, usr_length, msg_length, self.username.encode('utf-8'), self.message)

   def _decode_data(self, data):
      usr_length, msg_length = struct.unpack(self.format, data)
      packet_format = f'{self.format}{str(usr_length)}s{str(msg_length)}s'
      _, _, username, message = struct.unpack(packet_format, data)
      return UserMsgPacket(username.decode('utf-8'), message)
