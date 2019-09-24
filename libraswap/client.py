import time

import grpc

from libraswap.lib.admission_control_pb2 import (AdmissionControlStatusCode,
                                                 SubmitTransactionRequest)
from libraswap.lib.admission_control_pb2_grpc import AdmissionControlStub
from libraswap.lib.get_with_proof_pb2 import (
    GetAccountStateRequest, GetAccountTransactionBySequenceNumberRequest,
    RequestItem, UpdateToLatestLedgerRequest)
from libraswap.lib.transaction_pb2 import SignedTransaction
from libraswap.transaction.transaction import TRANSFER_OPCODE, Transaction
from libraswap.utils.hash import create_hasher, create_hasher_prefix
from libraswap.utils.verify import (verify_events, verify_tx_hash,
                                    verify_tx_proof)
from libraswap.wallet.account_state import AccountState


class LibraClient:
    def __init__(self, rpc_server):
        self.rpc_server = rpc_server
        self.last_version_seen = 0
        self.stub = self._start_rpc_client_instance()

    def _start_rpc_client_instance(self):
        channel = grpc.insecure_channel(self.rpc_server)
        return AdmissionControlStub(channel)

    def get_latest_version_from_ledger(self):
        request = UpdateToLatestLedgerRequest(
            client_known_version=self.last_version_seen, requested_items=[]
        )
        response = self.stub.UpdateToLatestLedger(request)
        ledger_version = response.ledger_info_with_sigs.ledger_info.version
        self.last_version_seen = ledger_version
        return ledger_version

    def get_account_state(self, addr):
        account = GetAccountStateRequest(address=bytes.fromhex(addr))
        item = RequestItem(get_account_state_request=account)
        request = UpdateToLatestLedgerRequest(
            client_known_version=self.last_version_seen, requested_items=[item]
        )
        response = self.stub.UpdateToLatestLedger(request)
        state = response.response_items[0].get_account_state_response
        raw_data = state.account_state_with_proof.blob.blob
        if len(raw_data) == 0:
            return AccountState.empty(addr)
        else:
            return AccountState.from_bytes(raw_data)

    def get_account_transaction(self, address, seq, fetch_events=None):
        tx_req = GetAccountTransactionBySequenceNumberRequest(account=bytes.fromhex(address), sequence_number=seq, fetch_events=True)
        item = RequestItem(get_account_transaction_by_sequence_number_request=tx_req)
        request = UpdateToLatestLedgerRequest(
            client_known_version=self.last_version_seen, requested_items=[item])
        response = self.stub.UpdateToLatestLedger(request)

        tx_with_proof = response.response_items[0].get_account_transaction_by_sequence_number_response.signed_transaction_with_proof
        root = response.ledger_info_with_sigs.ledger_info.transaction_accumulator_hash

        tx_version = tx_with_proof.version
        tx_info = tx_with_proof.proof.transaction_info
        tx_hash = tx_info.signed_transaction_hash
        tx = tx_with_proof.signed_transaction
        proof = tx_with_proof.proof.ledger_info_to_transaction_info_proof

        verify_events(tx_with_proof.events.events)
        verify_tx_hash(tx, tx_hash)
        verify_tx_proof(tx_info, tx_version, proof, root)
        return root, tx_version, tx_with_proof.proof

    def send_transaction(self, sender, recipient, amount, max_gas_amount=140000, gas_unit_price=0, expiration_time=None):
        if expiration_time is None:
            expiration_time = int(time.time()) + 10

        account_state = self.get_account_state(sender.address)
        seq = account_state.sequence_number

        tx = Transaction(sender.address, seq, max_gas_amount, gas_unit_price,
                         expiration_time, recipient.address, amount, TRANSFER_OPCODE)

        m = create_hasher()
        m.update(create_hasher_prefix(b'RawTransaction'))
        m.update(tx.raw_tx_bytes)
        raw_tx_hash = m.digest()

        signed_txn = SignedTransaction()
        signed_txn.sender_public_key = bytes.fromhex(sender.public_key)
        signed_txn.raw_txn_bytes = tx.raw_tx_bytes
        signed_txn.sender_signature = sender.sign(raw_tx_hash)[:64]

        request = SubmitTransactionRequest(signed_txn=signed_txn)
        response = self.stub.SubmitTransaction(request)
        if response.ac_status.code != AdmissionControlStatusCode.Accepted:
            raise Exception('Transaction has been rejected by admission control')
        return response
