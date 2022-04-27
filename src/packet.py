from abc import abstractmethod
import struct, enum

PACKET_SWITCH = dict()

class UnknownPacketTypeError(Exception):
	"""Thrown if an unknown packet type is encountered"""
	pass


class MalformedPacketError(Exception):
	"""Thrown if a packet is unable to be parsed"""
	pass


class PacketType(enum.IntEnum):
   USER_JOIN = 1
   USER_TERMINATE = 2
   USER_MESSAGE = 3
   INVALID = 4

class Packet:
   type = PacketType.INVALID
   header_format = '<HI' # < - little endian,  H - unsigned short, I - unsigned int
   header_size = struct.calcsize(header_format)

   def decode(self, raw_data):
      if len(raw_data) < self.header_size:
         raise UnknownPacketTypeError('Length of data is too short')
      type_id, data_length = struct.unpack(
          self.header_format, raw_data[:self.header_size])
      # verify the payload is fully in the buffer
      if len(raw_data[self.header_size:]) < data_length:
         raise MalformedPacketError('Packet payload is too short')
      payload = raw_data[self.header_size:self.header_size + data_length]
      yield PACKET_SWITCH[type_id]._decode_data(payload)
      # remaining data to be processed - recursive call
      remaining_data = raw_data[self.header_size + data_length:]
      if len(remaining_data) > 0:
         yield from self.decode(remaining_data)

   @abstractmethod
   def _decode_data(self, payload):
      pass

   @abstractmethod
   def _encode_data(self):
      pass

   def encode(self):
      payload = self._encode_data()
      header = struct.pack(self.header_format, int(self.type), len(payload))
      return header + payload


class UserJoinPacket(Packet): # this packet is send by the client/receive by the server when they first connect
   type = PacketType.USER_JOIN
   format = '<H'
   format_size = struct.calcsize(format)

   def __init__(self, username):
      self.username = username

   def _encode_data(self):
      length = len(self.username)
      packet_format = f'{self.format}{str(length)}s'
      return struct.pack(packet_format, length, self.username.encode('utf-8'))

   @classmethod
   def _decode_data(self, data):
      length = struct.unpack(self.format, data[:self.format_size])[0]
      packet_format = f'{self.format}{str(length)}s'
      length, username = struct.unpack(packet_format, data)
      return UserJoinPacket(username.decode('utf-8'))


PACKET_SWITCH[UserJoinPacket.type] = UserJoinPacket


class UserTerminatePacket(Packet): # this packet is send by the client/receive by the server when a client disconnect to the server
   type = PacketType.USER_TERMINATE
   format = '<H'
   format_size = struct.calcsize(format)

   def __init__(self, username):
      self.username = username

   def _encode_data(self):
      length = len(self.username)
      packet_format = f'{self.format}{str(length)}s'
      return struct.pack(packet_format, length, self.username.encode('utf-8'))

   @classmethod
   def _decode_data(self, data):
      length = struct.unpack(self.format, data[:self.format_size])[0]
      packet_format = f'{self.format}{str(length)}s'
      length, username = struct.unpack(packet_format, data)
      return UserTerminatePacket(username.decode('utf-8'))

PACKET_SWITCH[UserTerminatePacket.type] = UserTerminatePacket


class UserMsgPacket(Packet):
   type = PacketType.USER_MESSAGE
   format = '<HH'
   format_size = struct.calcsize(format)

   def __init__(self, username, msg):
      self.username = username
      self.message = msg

   def _encode_data(self):
      usr_length = len(self.username)
      msg_length = len(self.message)
      packet_format = f'{self.format}{str(usr_length)}s{str(msg_length)}s'
      return struct.pack(packet_format, usr_length, msg_length, self.username.encode('utf-8'), self.message)

   @classmethod
   def _decode_data(self, data):
      usr_length, msg_length = struct.unpack(
          self.format, data[:self.format_size])
      packet_format = f'{self.format}{str(usr_length)}s{str(msg_length)}s'
      _, _, username, message = struct.unpack(packet_format, data)
      return UserMsgPacket(username.decode('utf-8'), message)

PACKET_SWITCH[UserMsgPacket.type] = UserMsgPacket

class UserDupPacket(UserMsgPacket):
   type = PacketType.INVALID
   pass

PACKET_SWITCH[UserDupPacket.type] = UserDupPacket
