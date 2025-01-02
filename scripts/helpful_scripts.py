from brownie import network, config, accounts
from web3 import Web3
import math
import time

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganace-local", "mainnet-fork"]
TESTNETS = ["goerli"]

"""Retrives an account. 

   Args:    
        index (int): index returns a local ganache account
        id (int): return one of the accounts saved for rinkeby use. Keys must be in .env file
        
    Returns:
        account xor none if something went wrong. 

"""


def get_account(index=None, id=None, number=None):
    # accounts[0]
    # accounts.add("env")
    # account.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)  # id="freecodecamp-account"
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if network.show_active() in config["networks"]:
        if number:
            if number == 0:
                return accounts.add(config["wallets"][f"from_key"])
            else:
                return accounts.add(config["wallets"][f"from_key{number}"])
        else:
            return accounts.add(config["wallets"]["from_key"])
    else:
        return None


"""hashes 2 strings concatenating them and encoding them as solidity woould do it. 
    The first string must be the secret and the second the offer amount

   Args:
        s1 (string): secret word
        s2 (string): amount offered in wei.
        
    Returns:
        hashed string

"""


def hashStrings(s1, s2):
    ans = Web3.solidity_keccak(["bytes32", "uint256"], [bytes(s1, "utf-8"), int(s2)])
    return ans


"""Function to get the actual UNIX time
        
    Returns:
        unix timestamp in seconds (int) of right now. 

"""


def time_now():
    return math.floor(time.time())


def main():
    print(hashStrings("secreto", Web3.to_wei(1.23, "ether")).hex())


# price = Web3.to_wei(0.16, 'ether')
# secret = 'Secret1'
# ans = hashStrings(secret,price)
# print(ans)
# print(Web3.toBytes(text=secret))
# print(price)
# ans = hashStrings(secret,price)
# ans = Web3.solidity_keccak(['bytes32','uint256'],[bytes('Secret1','utf-8'), 160000000000000000])
# print(ans.hex())
