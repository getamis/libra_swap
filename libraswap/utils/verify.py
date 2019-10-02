from libraswap.utils.hash import create_hasher, create_hasher_prefix
from libraswap.transaction.transaction_info import TransactionInfo

ACCUMULATOR_PLACEHOLDER = b'ACCUMULATOR_PLACEHOLDER_HASH\000\000\000\000'


def verify_events(events):
    # peer-to-peer transfer will emit one sent event and one received event.
    assert len(events) == 2


def verify_tx_proof(tx_info, tx_version, proof, root):
    info = TransactionInfo(
        tx_info.signed_transaction_hash,
        tx_info.state_root_hash,
        tx_info.event_root_hash,
        tx_info.gas_used,
        tx_info.major_status
    )

    # tx_info = Hash(signed_tx, state_root, event_root, gas_used, major_status)
    m = create_hasher()
    m.update(create_hasher_prefix(b'TransactionInfo'))
    m.update(info.serialize())
    result = m.digest()

    bitmap = proof.bitmap
    siblings = proof.non_default_siblings[:]
    while bitmap > 0:
        # tree_node = Hash(left_child, right_child)
        m = create_hasher()
        m.update(create_hasher_prefix(b'TransactionAccumulator'))
        sibling = ACCUMULATOR_PLACEHOLDER if bitmap % 2 == 0 else siblings.pop()
        if tx_version % 2 == 0:
            m.update(result)
            m.update(sibling)
        else:
            m.update(sibling)
            m.update(result)
        result = m.digest()

        bitmap //= 2
        tx_version //= 2
    assert len(siblings) == 0
    assert result == root


def verify_tx_hash(tx, tx_hash):
    # tx_hash = Hash(signed_txn)
    m = create_hasher()
    m.update(create_hasher_prefix(b'SignedTransaction'))
    m.update(tx.signed_txn)

    assert m.digest() == tx_hash
