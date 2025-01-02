from brownie import SealedBidAuction
from web3 import Web3
from scripts.helpful_scripts import get_account
from scripts.deploy_auction import 
from scripts.manage_nft import last_nft
MIN_PRICE = Web3.to_wei(0.1, 'ether')
SECRET = "thisIsASecret"

'''Script used to read the last deployed contrct, used mostly for debugging. 
    The current version is the last one used, that does not mean it works.

'''
def main():
    accounts = [get_account(number=0),get_account(number=1),get_account(number=2)]
    secrets = ["S1", "S2", "S3"]
    prices = [Web3.to_wei(0.01, 'ether'),Web3.to_wei(0.4, 'ether'),Web3.to_wei(0.5, 'ether')]
    initial_balances = [accounts[0].balance(), accounts[1].balance(), accounts[2].balance()]
    contract = SealedBidAuction[-1]
    collectible, collectible_number = last_nft()
    tx = contract.winnerRetrivesToken({"from": accounts[2]})
    tx.wait(0)
    # Loser reinburses
    tx = contract.reimburseParticipant({"from": accounts[1]})
    tx.wait(0)
    # auctioneer gets payed
    tx = contract.ownerGetsPayed({"from": accounts[0]})
    tx.wait(0)