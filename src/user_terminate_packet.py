from src.packet import Packet, PacketType
import struct


class UserTerminatePacket(Packet):
   def __init__(self, username):
      self.type = PacketType.USER_TERMINATE
      self.format = '<H'
      self.username = username

   def _encode_data(self):
      length = len(self.username)
      packet_format = f'{self.format}{str(length)}s'
      return struct.pack(packet_format, length, self.username.encode('utf-8'))

   def _decode_data(self, data):
      length = struct.unpack(self.format, data)[0]
      packet_format = f'{self.format}{str(length)}s'
      length, username = struct.unpack(packet_format, data)
      return UserTerminatePacket(username.decode('utf-8'))
