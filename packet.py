import struct
import enum
import time
import typing

PACKET_TYPE_CLASS_MAP = dict()

class UnknownPacketTypeError(Exception):
	"""Thrown if an unknown packet type is encountered"""
	pass

class MalformedPacketError(Exception):
	"""Thrown if a packet is unable to be parsed"""
	pass

class PacketType(enum.IntEnum):
	"""Valid packet types"""

	USER_JOIN = 0x00
	USER_DISCONNECT = 0x01
	USER_MESSAGE = 0x02
	KEEPALIVE = 0x03
	INVALID = enum.auto()

class Packet:
	"""General packet wrapper class"""

	_type = PacketType.INVALID
	_id = int(_type)

	_HEADER_PACK_STR = '<HI'
	_HEADER_SIZE = struct.calcsize(_HEADER_PACK_STR)

	@classmethod
	def decode(cls, data: bytes):
		"""Decode a bytes object into a series of packets

		This function is a generator, as it's possible for multiple packets to be received in one
		class to socket.recv().

		To consume:
		```
		for packet in Packet.decode(data):
			print(packet)
		```
		"""

		if len(data) < cls._HEADER_SIZE:
			raise MalformedPacketError('Not enough data in packet')
		_id, length = struct.unpack(cls._HEADER_PACK_STR, data[:cls._HEADER_SIZE])
		if _id not in PACKET_TYPE_CLASS_MAP:
			raise UnknownPacketTypeError('Unknown packet type: {}'.format(_id))
		if len(data[cls._HEADER_SIZE:]) < length:
			raise MalformedPacketError('Not enough data in packet body')
		
		packet_data = data[cls._HEADER_SIZE:cls._HEADER_SIZE + length]
		yield PACKET_TYPE_CLASS_MAP[_id]._decode_data(packet_data)

		leftover_data = data[cls._HEADER_SIZE + length:]
		if leftover_data:
			yield from cls.decode(leftover_data)
	
	@classmethod
	def _decode_data(cls, _data: bytes):
		"""Handles actually decoding the packet data
		
		Should not be called from client code. Instead, use the generic `Packet.decode()` function,
		which will decode the packet header and select the correct packet type based on its ID.
		"""

		raise NotImplementedError()
		
	def encode(self):
		"""Encode the packet into a bytes object suitable for sending over the network
		
		Example usage:
		```
		packet = UserMessagePacket(UserMessagePacket.EncryptionScheme.AES, 'bob', b'Hello, world!')
		data = packet.encode()
		socket.send(data) # or whatever
		```
		"""

		data = self._encode_data()
		header = struct.pack(self._HEADER_PACK_STR, self._id, len(data))
		return header + data
	
	def _encode_data(self, _data: bytes):
		"""Handles actually encoding the packet's data
		
		Should not be called from client code. Instead, use the generic `Packet.encode()` function,
		which will prepend the packet header to the encoded packet.
		"""

		raise NotImplementedError()
	
	def _str(self):
		"""Return a string representation of the packet's unique data

		Any generic information (eg, type) is included by the Packet's `__str__` implementation.
		"""

		raise NotImplementedError()

	def __str__(self):
		return f'{repr(self._type)}: {self._str()}'

class UserJoinPacket(Packet):
	"""Packet type sent when a user joins the network"""

	_type = PacketType.USER_JOIN
	_id = int(_type)
	
	def __init__(self, usr: str):
		"""Constructs a new UserJoinPacket
		
		Args:
			usr (str): The username of the user who joined
		"""
		self.username = usr
	
	def _encode_data(self):
		length = len(self.username)
		pack_str = f'<H{str(length)}s'
		return struct.pack(pack_str, length, self.username.encode('utf-8'))

	@classmethod
	def _decode_data(cls, data: bytes):
		length = struct.unpack_from('<H',data)[0]
		pack_str = f'<H{str(length)}s'
		length, username = struct.unpack(pack_str, data)
		return UserJoinPacket(username.decode('utf-8'))
	
	def _str(self):
		return self.username

PACKET_TYPE_CLASS_MAP[UserJoinPacket._id] = UserJoinPacket

class UserDisconnectPacket(Packet):
	"""Packet sent when a user disconnects from the network"""

	_type = PacketType.USER_DISCONNECT
	_id = int(_type)
	
	@enum.unique
	class DisconnectionReason(enum.IntEnum):
		"""Reason for a user disconnecting from the network
		
		LEAVE: User disconnected cleanly (closed their client)
		TIMEOUT: User lost connection to the server
		"""

		LEAVE = 0
		TIMEOUT = 1

	def __init__(self, reason: DisconnectionReason, usr: str):
		"""Constructs a new UserDisconnectPacket

		Args:
			reason (DisconnectionReason): The reason for the user disconnecting
			usr (str): The username of the user who disconnected
		"""

		self.disconnect_reason = reason
		self.username = usr
	
	def _encode_data(self):
		length = len(self.username)
		pack_str = f'<HH{str(length)}s'
		return struct.pack(pack_str, int(self.disconnect_reason), length, self.username.encode('utf-8'))
	
	@classmethod
	def _decode_data(cls, data: bytes):
		dc_reason, length = struct.unpack_from('<HH',data)
		pack_str = f'<HH{str(length)}s'
		_, _, username = struct.unpack(pack_str,data)
		return UserDisconnectPacket(cls.DisconnectionReason(dc_reason), username.decode('utf-8'))
	
	def _str(self):
		return f'{self.username=}, {self.disconnect_reason=}'

PACKET_TYPE_CLASS_MAP[UserDisconnectPacket._id] = UserDisconnectPacket

class UserMessagePacket(Packet):
	"""Packet sent when a user sends a message"""

	_type = PacketType.USER_MESSAGE
	_id = int(_type)
	
	@enum.unique
	class EncryptionScheme(enum.IntEnum):
		"""Represents the set of allowable message encryption schemes used by a message"""

		CAESAR = 0
		AES = 1
		PLAINTEXT = 2

	def __init__(self, enc: EncryptionScheme, usr: str, msg: bytes):
		"""Constructs a new UserMessagePacket
		
		Args:
			enc (EncryptionScheme): The encryption scheme used to encrypt the message
			usr (str): The username of the user who sent the message
			msg (bytes): The message sent by the user
		"""

		self.encryption = enc
		self.username = usr
		self.message = msg
	
	def _encode_data(self):
		message_length = len(self.message)
		username_length = len(self.username)
		pack_str = f'<HHH{str(username_length)}s{str(message_length)}s'
		return struct.pack(pack_str, int(self.encryption), username_length, message_length, self.username.encode('utf-8'), self.message)

	@classmethod
	def _decode_data(cls, data: bytes):
		enc, username_length, message_length  = struct.unpack_from('<HHH', data)
		pack_str = f'<HHH{str(username_length)}s{str(message_length)}s'
		_, _, _, username, message = struct.unpack(pack_str, data)
		return UserMessagePacket(cls.EncryptionScheme(enc), username.decode('utf-8'), message)
	
	def _str(self):
		return f'{self.encryption=}, {self.message=}'

PACKET_TYPE_CLASS_MAP[UserMessagePacket._id] = UserMessagePacket

class KeepAlivePacket(Packet):
	"""Packet sent periodically to keep the TCP socket alive"""

	_type = PacketType.KEEPALIVE
	_id = int(_type)
	
	def __init__(self, ts: typing.Optional[int]=None):
		"""Constructs a new KeepAlivePacket

		Args:
			ts (int | None): The UNIX timestamp of when the packet was sent
		"""

		self.timestamp = ts or int(time.time())
	
	def _encode_data(self):
		return struct.pack('<I', self.timestamp)

	@classmethod
	def _decode_data(cls, data: bytes):
		ts, = struct.unpack('<I', data)
		return KeepAlivePacket(ts)
	
	def _str(self):
		return f'{self.timestamp=}'

PACKET_TYPE_CLASS_MAP[KeepAlivePacket._id] = KeepAlivePacket
