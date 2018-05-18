from random import randint
from web3 import Web3, TestRPCProvider, HTTPProvider
from solc import compile_source
from web3.contract import ConciseContract
from web3 import Account
import requests
import time
import os
import json


def compile_source_file(file_path):
    with open(file_path, 'r') as f:
        source = f.read()
    return compile_source(source)


class TokenERC20Factory(object):
    PRIVATE_KEY = os.environ['PRIVATE_KEY']
    ADDRESS = os.environ['ADDRESS']

    def __init__(self, name, symbol, total_supply):
        self.name = name
        self.symbol = symbol
        self.total_supply = total_supply

    def deploy_contract(self):
        compiled_sol = compile_source_file('TokenERC20.sol')
        contract_interface = compiled_sol['<stdin>:TokenERC20']

        # web3.py instance
        w3 = Web3(HTTPProvider('https://rinkeby.infura.io/SKMV9xjeMbG3u7MnJHVH'))

        # Instantiate and deploy contract
        contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

        with open('contract_abi.json', 'w') as outfile:
            json.dump(contract_interface['abi'], outfile)

        data = contract._encode_constructor_data(args=(self.total_supply, self.name, self.symbol))
        transaction = {'data': data,
                       'gas': 3000001,
                       'gasPrice': 8000001,
                       'chainId': 4,
                       'to': '',
                       'from': self.ADDRESS,
                       'nonce': w3.eth.getTransactionCount(self.ADDRESS)}
        acct = Account.privateKeyToAccount(self.PRIVATE_KEY)
        signed = acct.signTransaction(transaction)
        tx = w3.eth.sendRawTransaction(signed.rawTransaction)
        tx_hash = w3.toHex(tx)
        return tx_hash


def transfer(contract_address, to, amount):
    with open(os.path.join('./contract_abi.json'), 'r') as abi_definition:
        abi = json.load(abi_definition)

    w3 = Web3(HTTPProvider('https://rinkeby.infura.io/SKMV9xjeMbG3u7MnJHVH'))

    contract = w3.eth.contract(address=contract_address, abi=abi)

    unicorn_txn = contract.functions.transfer(to, amount * 1000000000000000000).buildTransaction({
        'value': 0,
        'gas': w3.toHex(1000001),
        'gasPrice': w3.toWei('10000', 'gwei'),
        'nonce': w3.eth.getTransactionCount('0x6f212bF41DF64De9782dbfb26112BD3B0e39514B'),
        'from': '0x6f212bF41DF64De9782dbfb26112BD3B0e39514B'
    })

    private_key = r"955ca0f797c309aadd06d6bd9272ed71e57210ea145edff4b238c3db0b63f219"
    acct = Account.privateKeyToAccount(private_key)
    signed = acct.signTransaction(unicorn_txn)
    tx = w3.eth.sendRawTransaction(signed.rawTransaction)
    tx_hash = w3.toHex(tx)
    return tx_hash


# print(TokenERC20Factory('Tin coin', 'TIN', 100000000).deploy_contract())
print(transfer('0x2AA6203b4EdD2CbD55e166d88b5E422dB5A77f38', '0x6f212bF41DF64De9782dbfb26112BD3B0e39514B', 100000))
