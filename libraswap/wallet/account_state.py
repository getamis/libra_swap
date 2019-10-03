from canoser import Struct
from canoser.types import *


# FIXME: I don't know how exactly to generate the account state path yet.
#        This value is fixed so we make a constance here.
#        However, since we are using keccak256, the value should be changed if
#        we use sha3-256.
ACCOUNT_STATE_PATH = '01296d2b26a8976ed85bbb78f1e8a7b424499a1a91a5189c9d2c36cda6d74a252d'

class EventHandle(Struct):
    _fields = [
        ('count', Uint64),
        ('key', [Uint8])
    ]

    @staticmethod
    def empty():
        return EventHandle(0, [])


class AccountResource(Struct):
    _fields = [
        ('authentication_key', [Uint8]),
        ('balance', Uint64),
        ('delegated_key_rotation_capability', bool),
        ('delegated_withdrawal_capability', bool),
        ('received_events', EventHandle),
        ('sent_events', EventHandle),
        ('sequence_number', Uint64)
    ]

    @property
    def address(self):
        return bytes(self.authentication_key).hex()

    @staticmethod
    def empty(address):
        if isinstance(address, str):
            address = bytes.fromhex(address)
        if isinstance(address, bytes):
            address = list(address)
        return AccountResource(address, 0, False, False, EventHandle.empty(), EventHandle.empty(), 0)

    def __str__(self):
        return f'''address: {self.address}
balance: {self.balance}
delegated_key_rotation_capability: {self.delegated_key_rotation_capability}
delegated_withdrawal_capability: {self.delegated_withdrawal_capability}
received_events_count: {self.received_events.count}
sent_events_count: {self.sent_events.count}
sequence_number: {self.sequence_number}'''


class AccountState(Struct):
    _fields = [
        ('blob', {})
    ]
