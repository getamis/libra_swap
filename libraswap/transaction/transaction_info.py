from canoser import Struct
from canoser.types import *


class TransactionInfo(Struct):
    _fields = [
        ('signed_transaction_hash', [Uint8]),
        ('state_root_hash', [Uint8]),
        ('event_root_hash', [Uint8]),
        ('gas_used', Uint64),
        ('major_status', Uint64)
    ]
