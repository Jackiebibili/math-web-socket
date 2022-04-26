from abc import abstractmethod
import struct, enum


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
   def __init__(self):
      self.type = PacketType.INVALID
      self.header_format = '<HI' # < - little endian,  H - unsigned short, I - unsigned int
      self.header_size = struct.calcsize(self.header_format)

   def decode(self, raw_data):
      if len(raw_data) < self.header_size:
         raise UnknownPacketTypeError('Length of data is too short')
      type_id, data_length = struct.unpack(
          self.header_format, raw_data[:self.header_size])
      # verify the payload is fully in the buffer
      if len(raw_data[self.header_size]) < data_length:
         raise MalformedPacketError('Packet payload is too short')
      payload = raw_data[self.header_size:self.header_size + data_length]
      yield self._decode_data(payload)
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
      payload = self._decode_data()
      header = struct.pack(self.header_format, int(self.type), len(payload))
      return header + payload


