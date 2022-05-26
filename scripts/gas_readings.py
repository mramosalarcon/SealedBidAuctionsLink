from brownie import network, config, SealedBidAuction, CollectibleCreator
from scripts.helpful_scripts import  get_account, hashStrings
from web3 import Web3
from scripts.manage_nft import last_nft


'''

    Methods in this file are for averaging the gas prices in a complete auction. 
    Turns out I forgot I did not do it 


'''

# TODO 


MIN_PRICE = Web3.toWei(0.1, 'ether')
SECRET = "thisIsASecret"
METADATA = "https://ipfs.io/ipfs/QmR6xprTY253fDPM423C5t3EjdTVXuqPDXjPJhpp7v7gQc"

'''Desc

   Args:
        
    Returns:

'''
