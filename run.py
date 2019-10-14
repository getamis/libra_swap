"""Libra swap.

Usage:
  run.py deploy_contract
  run.py deposit [--depositor=<depositor>] [--beneficiary=<beneficiary>]
  run.py query_deposit [--deposit_id=<deposit_id>]
  run.py transfer_1_lib [--from=<from>] [--to=<to>]
  run.py transfer_1_eth [--depositor=<depositor>] [--deposit_id=<deposit_id>]
  run.py challenge [--from=<from>] [--from_sequence=<from_sequence>] [--deposit_id=<deposit_id>]
  run.py (-h | --help | --usage)
  run.py --version
"""
import json
import os
import time

from docopt import docopt
from web3.auto import w3

from contract import deploy_contract, get_contract
from libraswap.client import LibraClient
from libraswap.transaction.transaction_info import TransactionInfo
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

    show_balance(libra, lib_account1, lib_account2, eth_account1, eth_account2)

    if arguments['deploy_contract']:
        libra_contract = deploy_contract('Libra')

        # write contract addresses to config file for convenience
        config = load_config()
        config['LIBRA_CONTRACT_ADDRESS'] = libra_contract.address
        update_config(config)
    elif arguments['deposit']:
        depositor_address = eth_account1 if arguments['--depositor'] == 'A' else eth_account2
        beneficiary_address = eth_account1 if arguments['--beneficiary'] == 'A' else eth_account2
        contract_address = load_config()['LIBRA_CONTRACT_ADDRESS']

        libra_contract = get_contract('Libra', contract_address)

        # deposit(address beneficiary)
        tx_hash = libra_contract.functions.deposit(
            beneficiary_address,
        ).transact({
            'from': depositor_address,
            'value': w3.toWei(2, 'ether'),
        })

        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        deposit_logs = libra_contract.events.DepositEvent().processReceipt(tx_receipt)
        log = dict(dict(deposit_logs[0])['args'])

        assert log['depositor'] == depositor_address
        assert log['beneficiary'] == beneficiary_address

        print(f"account {arguments['--depositor']} deposits 2 ethers to contract with deposit ID {log['depositID']}, and specifies beneficiary to account {arguments['--beneficiary']}\n")
    elif arguments['query_deposit']:
        deposit_id = int(arguments['--deposit_id'])
        contract_address = load_config()['LIBRA_CONTRACT_ADDRESS']

        libra_contract = get_contract('Libra', contract_address)

        deposit = libra_contract.functions.deposits(
            deposit_id
        ).call()
        print(f"depositor: {deposit[0]}\nbeneficiary: {deposit[1]}\namount: {w3.fromWei(deposit[2], 'ether')}\nstart time: {deposit[3]}\nrefund time: {deposit[4]}\n")
    elif arguments['transfer_1_lib']:
        from_account = lib_account1 if arguments['--from'] == 'A' else lib_account2
        to_account = lib_account1 if arguments['--to'] == 'A' else lib_account2

        lib_state = libra.get_account_state(from_account.address)
        if lib_state.balance == 0:
            raise Exception('Please mint some LIB to address A manually')

        libra.send_transaction(from_account, to_account, 1 * LIB)

        print(f"Transaction has been sent from account {arguments['--from']} with sequence {lib_state.sequence_number}\n")

        time.sleep(3)
    elif arguments['transfer_1_eth']:
        depositor_eth_address = eth_account1 if arguments['--depositor'] == 'A' else eth_account2
        deposit_id = int(arguments['--deposit_id'])
        contract_address = load_config()['LIBRA_CONTRACT_ADDRESS']

        libra_contract = get_contract('Libra', contract_address)

        print(f"Libra payment is confirmed. {arguments['--depositor']} will send 1 ether to beneficiary and get the remaining deposit.\n")

        # transfer(uint256 depositID, uint amount)
        tx_hash = libra_contract.functions.transfer(
            deposit_id,
            w3.toWei(1, 'ether')
        ).transact({
            'from': depositor_eth_address,
        })
    elif arguments['challenge']:
        from_lib_account = lib_account1 if arguments['--from'] == 'A' else lib_account2
        from_sequence = int(arguments['--from_sequence'])
        from_eth_address = eth_account1 if arguments['--from'] == 'A' else eth_account2
        deposit_id = int(arguments['--deposit_id'])
        contract_address = load_config()['LIBRA_CONTRACT_ADDRESS']

        libra_contract = get_contract('Libra', contract_address)

        # get transaction infomation
        root, tx_version, proof = libra.get_account_transaction(from_lib_account.address, from_sequence)
        tx_info = TransactionInfo(
            proof.transaction_info.signed_transaction_hash,
            proof.transaction_info.state_root_hash,
            proof.transaction_info.event_root_hash,
            proof.transaction_info.gas_used,
            proof.transaction_info.major_status
        )

        # challenge(uint256 depositID, bytes memory txInfo, bytes32 root, bytes32[] memory proof, uint256 txVersion, uint256 bitmap)
        tx_hash = libra_contract.functions.challenge(
            deposit_id,
            tx_info.serialize().hex(),
            root.hex(),
            [p.hex() for p in proof.ledger_info_to_transaction_info_proof.non_default_siblings],
            tx_version,
            proof.ledger_info_to_transaction_info_proof.bitmap
        ).transact({
            'from': from_eth_address,
        })

        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        print(f"Account {arguments['--from']} challenges successfully.\n")
    show_balance(libra, lib_account1, lib_account2, eth_account1, eth_account2)


if __name__ == '__main__':
    main()
