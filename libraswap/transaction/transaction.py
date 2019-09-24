from libraswap.lib.transaction_pb2 import RawTransaction, TransactionArgument


# You could compile these codes (https://github.com/libra/libra/blob/master/language/stdlib/transaction_scripts/)
# locally and convert the bytes code to hex string to get these values.
TRANSFER_OPCODE = '4c49425241564d0a010007014a00000004000000034e000000060000000c54000000060000000d5a0000000600000005600000002900000004890000002000000007a90000000f00000000000001000200010300020002040200030003020402063c53454c463e0c4c696272614163636f756e74046d61696e0f7061795f66726f6d5f73656e6465720000000000000000000000000000000000000000000000000000000000000000000100020104000c000c0113010002'
MINT_OPCODE = '4c49425241564d0a010007014a000000060000000350000000060000000c56000000060000000d5c0000000600000005620000003300000004950000002000000007b50000000f000000000000010002000300010400020002040200030003020402063c53454c463e0c4c696272614163636f756e74094c69627261436f696e046d61696e0f6d696e745f746f5f616464726573730000000000000000000000000000000000000000000000000000000000000000000100020104000c000c0113010002'


class Transaction:
    def __init__(
        self,
        sender,
        sequence,
        max_gas_amount,
        gas_unit_price,
        expiration_time,
        recipient,
        amount,
        opcode
    ):
        self.sender = bytes.fromhex(sender)
        self.recipient = bytes.fromhex(recipient)
        self.amount = amount
        self.sequence = sequence
        self.max_gas_amount = max_gas_amount
        self.gas_unit_price = gas_unit_price
        self.expiration_time = expiration_time
        self.opcode = opcode

    @property
    def raw_tx_bytes(self):
        raw_tx = RawTransaction()
        raw_tx.sender_account = self.sender
        raw_tx.sequence_number = self.sequence
        raw_tx.program.code = bytes.fromhex(self.opcode)
        arg1 = raw_tx.program.arguments.add()
        arg1.type = TransactionArgument.ADDRESS
        arg1.data = self.recipient
        arg2 = raw_tx.program.arguments.add()
        arg2.type = TransactionArgument.U64
        arg2.data = self.amount.to_bytes(8, 'little')
        raw_tx.max_gas_amount = self.max_gas_amount
        raw_tx.gas_unit_price = self.gas_unit_price
        raw_tx.expiration_time = self.expiration_time
        return raw_tx.SerializeToString()
