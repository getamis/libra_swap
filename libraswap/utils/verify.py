from libraswap.utils.hash import create_hasher, create_hasher_prefix

ACCUMULATOR_PLACEHOLDER = b'ACCUMULATOR_PLACEHOLDER_HASH\000\000\000\000'


def verify_events(events):
    # peer-to-peer transfer will emit one sent event and one received event.
    assert len(events) == 2


def verify_tx_proof(tx_info, tx_version, proof, root):
    signed_tx_len = len(tx_info.signed_transaction_hash)
    state_root_len = len(tx_info.state_root_hash)
    event_root_len = len(tx_info.event_root_hash)

    # tx_info = Hash(signed_tx, state_root, event_root, gas_used)
    m = create_hasher()
    m.update(create_hasher_prefix(b'TransactionInfo'))
    m.update(signed_tx_len.to_bytes(4, 'little'))
    m.update(tx_info.signed_transaction_hash)
    m.update(state_root_len.to_bytes(4, 'little'))
    m.update(tx_info.state_root_hash)
    m.update(event_root_len.to_bytes(4, 'little'))
    m.update(tx_info.event_root_hash)
    m.update(b'\x00' * 8)
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
    raw_tx_len = len(tx.raw_txn_bytes)
    pubkey_len = len(tx.sender_public_key)
    sig_len = len(tx.sender_signature)

    # tx_hash = Hash(raw_tx, pubkey, sig)
    m = create_hasher()
    m.update(create_hasher_prefix(b'SignedTransaction'))
    m.update(raw_tx_len.to_bytes(4, 'little'))
    m.update(tx.raw_txn_bytes)
    m.update(pubkey_len.to_bytes(4, 'little'))
    m.update(tx.sender_public_key)
    m.update(sig_len.to_bytes(4, 'little'))
    m.update(tx.sender_signature)

    assert m.digest() == tx_hash
