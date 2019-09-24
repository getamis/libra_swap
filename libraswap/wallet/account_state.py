from io import BytesIO


class AccountState:
    def __init__(
        self,
        authentication_key,
        balance,
        delegated_withdrawal_capability,
        received_events_count,
        sent_events_count,
        sequence_number
    ):
        self.authentication_key = authentication_key
        self.balance = balance
        self.delegated_withdrawal_capability = delegated_withdrawal_capability
        self.received_events_count = received_events_count
        self.sent_events_count = sent_events_count
        self.sequence_number = sequence_number

    @staticmethod
    def empty(address):
        return AccountState(address, 0, 0, 0, 0, 0)

    @staticmethod
    def from_bytes(data):
        buffer = BytesIO(data)

        # account blob = {blob_key: blob_value}
        blob_len = int.from_bytes(buffer.read(4), byteorder="little")

        # blob_key
        blob_key_len = int.from_bytes(buffer.read(4), byteorder="little")
        blob_key = buffer.read(blob_key_len).hex()

        # blob value
        blob_value_len = int.from_bytes(buffer.read(4), byteorder="little")

        # 1. authentication key (address)
        authentication_key_len = int.from_bytes(buffer.read(4), byteorder="little")
        authentication_key = buffer.read(authentication_key_len).hex()

        # 2. balance
        balance = int.from_bytes(buffer.read(8), byteorder="little")
        # 3. withdrawal capability
        delegated_withdrawal_capability = int.from_bytes(buffer.read(1), byteorder="little")

        # 4. received event count / key
        received_events_count = int.from_bytes(buffer.read(8), byteorder="little")
        received_event_key_len = int.from_bytes(buffer.read(4), byteorder="little")
        received_event_key = buffer.read(received_event_key_len).hex()

        # 5. sent event count / key
        sent_events_count = int.from_bytes(buffer.read(8), byteorder="little")
        sent_event_key_len = int.from_bytes(buffer.read(4), byteorder="little")
        sent_event_key = buffer.read(sent_event_key_len).hex()

        # 6. sequence number
        sequence_number = int.from_bytes(buffer.read(8), byteorder="little")

        return AccountState(
            authentication_key,
            balance,
            delegated_withdrawal_capability,
            received_events_count,
            sent_events_count,
            sequence_number
        )

    def __str__(self):
        return f'''authentication_key: {self.authentication_key}
balance: {self.balance}
delegated_withdrawal_capability: {self.delegated_withdrawal_capability}
received_events_count: {self.received_events_count}
sent_events_count: {self.sent_events_count}
sequence_number: {self.sequence_number}'''
