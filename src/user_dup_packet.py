from user_msg_packet import UserMsgPacket
from packet import PacketType

class UserDupPacket(UserMsgPacket):
   def __init__(self, username, msg):
      super().__init__(username, msg)
      self.type = PacketType.INVALID
