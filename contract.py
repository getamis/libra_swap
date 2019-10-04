from pathlib import Path

from solcx import compile_files
from web3.auto import w3


def get_contract_interface(contract_name):
    # contract path
    contract_dir = Path('contracts').absolute()
    contract_path = contract_dir / 'contracts' / f'{contract_name}.sol'
    interface_path = f'{contract_path}:{contract_name}'

    # compile contract
    compiled_sol = compile_files([contract_path])
    contract_interface = compiled_sol[interface_path]
    contract_abi = contract_interface['abi']
    contract_bytecode = contract_interface['bin']

    return contract_abi, contract_bytecode


def deploy_contract(contract_name):
    # get contract interface
    contract_abi, contract_bytecode = get_contract_interface(contract_name)

    # we use the last account provided by ganache to deploy contracts
    w3.eth.defaultAccount = w3.eth.accounts[9]

    # deploy
    contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    tx_hash = contract.constructor().transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    contract_address = tx_receipt.contractAddress

    print(f'Deploy {contract_name}.sol to "{contract_address}"\n')

    return contract(address=contract_address)


def get_contract(contract_name, contract_address):
    # get contract interface
    contract_abi, contract_bytecode = get_contract_interface(contract_name)

    return w3.eth.contract(address=contract_address, abi=contract_abi)
