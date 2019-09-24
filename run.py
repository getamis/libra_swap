"""Libra swap.

Usage:
  run.py deploy_contract
  run.py generate_secret [options]
  run.py initiate [--from=<from>] [--to=<to>] [--hashed_secret=<hashed_secret>]
  run.py transfer_lib [--from=<from>] [--to=<to>] [--amount=<amount>]
  run.py verify_lib_tx [--from=<from>] [--to=<to>] [--from_sequence=<from_sequence>]
  run.py redeem [--account=<account>] [--secret=<secret>]
  run.py (-h | --help | --usage)
  run.py --version

Options:
  --demo    Use default secret
"""
import json
import os
import time

from docopt import docopt
from web3.auto import w3

from contract import deploy_contract, get_contract
from libraswap.client import LibraClient
from libraswap.utils.hash import create_hasher
from libraswap.wallet.wallet import LibraWallet

ENTROPY = '129ada3066c8904cd8851a946c779534e57d309302a01b62f7f819c140345678'
LIB = 1000000


def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)


def update_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)


def show_balance(libra_client, lib_account1, lib_account2, eth_account1, eth_account2):
    lib_state1 = libra_client.get_account_state(lib_account1.address)
    lib_state2 = libra_client.get_account_state(lib_account2.address)
    eth_balance1 = w3.fromWei(w3.eth.getBalance(eth_account1), 'ether')
    eth_balance2 = w3.fromWei(w3.eth.getBalance(eth_account2), 'ether')

    print(f"A's LIB address: {lib_account1.address} ({lib_state1.balance / LIB})")
    print(f"B's LIB address: {lib_account2.address} ({lib_state2.balance / LIB})")
    print(f"A's ETH balance: {eth_account1} ({eth_balance1})")
    print(f"B's ETH balance: {eth_account2} ({eth_balance2})\n")


def main():
    # command line
    arguments = docopt(__doc__, version='AMIS Libra swap 0.1')

    libra = LibraClient(load_config()['RPC_SERVER'])

    # create accounts
    wallet = LibraWallet(bytes.fromhex(ENTROPY))

    lib_account1 = wallet.new_account(0)
    lib_account2 = wallet.new_account(1)
    eth_account1 = w3.eth.accounts[0]
    eth_account2 = w3.eth.accounts[1]

    if arguments['deploy_contract']:
        swap_contract = deploy_contract('AtomicSwap')
        libra_contract = deploy_contract('Libra')

        # write contract addresses to config file for convenience
        config = load_config()
        config['SWAP_CONTRACT_ADDRESS'] = swap_contract.address
        config['LIBRA_CONTRACT_ADDRESS'] = libra_contract.address
        update_config(config)
    elif arguments['generate_secret']:
        # generate secret
        if arguments['--demo'] is True:
            secret = b'\x9c\xd4\xb5]z\xae\x829'
        else:
            secret = os.urandom(8)

        m = create_hasher()
        m.update(secret)
        hashed_secret = m.digest()

        print(f'Secret: {secret.hex()}')
        print(f'Hashed secret: {hashed_secret.hex()}')
    elif arguments['initiate']:
        show_balance(libra, lib_account1, lib_account2, eth_account1, eth_account2)

        from_address = eth_account1 if arguments['--from'] == 'A' else eth_account2
        to_address = eth_account1 if arguments['--to'] == 'A' else eth_account2
        hashed_secret = arguments['--hashed_secret']
        contract_address = load_config()['SWAP_CONTRACT_ADDRESS']

        swap_contract = get_contract('AtomicSwap', contract_address)

        # initiate(address receiver, bytes32 hashedSecret)
        tx_hash = swap_contract.functions.initiate(
            to_address,
            hashed_secret,
        ).transact({
            'from': from_address,
            'value': w3.toWei(1, 'ether'),
        })

        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        initiated_swap_logs = swap_contract.events.Initiated().processReceipt(tx_receipt)
        log = dict(dict(initiated_swap_logs[0])['args'])

        assert log['initiator'] == from_address
        assert log['receiver'] == to_address

        print(f"account {arguments['--from']} initiates a transaction with hashedSecret {log['hashedSecret'].hex()} to account {arguments['--to']}\n")

        show_balance(libra, lib_account1, lib_account2, eth_account1, eth_account2)
    elif arguments['transfer_lib']:
        show_balance(libra, lib_account1, lib_account2, eth_account1, eth_account2)

        from_account = lib_account1 if arguments['--from'] == 'A' else lib_account2
        to_account = lib_account1 if arguments['--to'] == 'A' else lib_account2
        amount = int(arguments['--amount'])

        lib_state = libra.get_account_state(from_account.address)
        if lib_state.balance == 0:
            raise Exception('Please mint some LIB to address A manually')

        libra.send_transaction(from_account, to_account, amount * LIB)

        print(f"Transaction has been sent from account {arguments['--from']} with sequence {lib_state.sequence_number}\n")

        time.sleep(3)

        show_balance(libra, lib_account1, lib_account2, eth_account1, eth_account2)
    elif arguments['verify_lib_tx']:
        from_account = lib_account1 if arguments['--from'] == 'A' else lib_account2
        to_account = lib_account1 if arguments['--to'] == 'A' else lib_account2
        from_sequence = int(arguments['--from_sequence'])
        contract_address = load_config()['LIBRA_CONTRACT_ADDRESS']

        # get transaction infomation
        root, tx_version, proof = libra.get_account_transaction(from_account.address, from_sequence)

        libra_contract = get_contract('Libra', contract_address)

        from_address = eth_account1 if arguments['--from'] == 'A' else eth_account2
        # send to contract
        tx_hash = libra_contract.functions.doesTxExist(
            proof.transaction_info.signed_transaction_hash.hex(),
            proof.transaction_info.state_root_hash.hex(),
            proof.transaction_info.event_root_hash.hex(),
            root.hex(),
            [p.hex() for p in proof.ledger_info_to_transaction_info_proof.non_default_siblings],
            tx_version,
            proof.ledger_info_to_transaction_info_proof.bitmap
        ).transact({
            'from': from_address,
        })
        print(f"Libra transaction has passed the contract validation, tx hash: {tx_hash.hex()}")
        print(f"Now, account {arguments['--from']} can send secret to account {arguments['--to']} privately\n")
    elif arguments['redeem']:
        show_balance(libra, lib_account1, lib_account2, eth_account1, eth_account2)

        account = eth_account1 if arguments['--account'] == 'A' else eth_account2
        secret = arguments['--secret']
        contract_address = load_config()['SWAP_CONTRACT_ADDRESS']

        swap_contract = get_contract('AtomicSwap', contract_address)

        # redeem(bytes memory secret)
        tx_hash = swap_contract.functions.redeem(
            secret
        ).transact({
            'from': account,
        })

        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        print(f"Account {arguments['--account']} redeems successfully\n")

        show_balance(libra, lib_account1, lib_account2, eth_account1, eth_account2)


if __name__ == '__main__':
    main()
