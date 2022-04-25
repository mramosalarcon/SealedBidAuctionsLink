from brownie import SealedBidAuction, config, network, exceptions
from web3 import Web3
from scripts.helpful_scripts import TESTNETS, get_account, hashStrings
from scripts.deploy_auction import deploy_auction
from scripts.manage_nft import last_nft
import pytest

MIN_PRICE = Web3.toWei(0.1, 'ether')
SECRET = "thisIsASecret"

def main():
    accounts = [get_account(number=0),get_account(number=1),get_account(number=2)]
    secrets = ["S1", "S2", "S3"]
    prices = [Web3.toWei(0.01, 'ether'),Web3.toWei(0.4, 'ether'),Web3.toWei(0.5, 'ether')]
    initial_balances = [accounts[0].balance(), accounts[1].balance(), accounts[2].balance()]
    contract = SealedBidAuction[-1]
    collectible, collectible_number = last_nft()
    tx = contract.winnerRetrivesToken({"from": accounts[2]})
    tx.wait(0)
    # Loser reinburses
    tx = contract.reiburseParticipant({"from": accounts[1]})
    tx.wait(0)
    # auctioneer gets payed
    tx = contract.ownerGetsPayed({"from": accounts[0]})
    tx.wait(0)