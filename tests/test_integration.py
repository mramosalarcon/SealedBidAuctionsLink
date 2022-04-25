from brownie import SealedBidAuction, config, network, exceptions
from web3 import Web3
from scripts.helpful_scripts import TESTNETS, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, hashStrings
from scripts.deploy_auction import deploy_auction
from scripts.manage_nft import last_nft
import pytest

MIN_PRICE = Web3.toWei(0.1, 'ether')
SECRET = "thisIsASecret"

def test_integration():
    if network.show_active() not in TESTNETS:
        pytest.skip()
    accounts = [get_account(number=0),get_account(number=1),get_account(number=2)]
    secrets = ["S1", "S2", "S3"]
    prices = [Web3.toWei(0.01, 'ether'), Web3.toWei(0.11, 'ether'), Web3.toWei(0.12, 'ether')]
    initial_balances = [accounts[0].balance(), accounts[1].balance(), accounts[2].balance()]
    auction, initial_hash = deploy_auction()
    initial_auction_balance = auction.balance()
    collectible, collectible_id = last_nft()
    # Make ofers
    tx = auction.makeOffer(hashStrings(secrets[1], prices[1]), {'from': accounts[1], 'value': prices[1]})
    tx.wait(1)
    tx = auction.makeOffer(hashStrings(secrets[2], prices[2]), {'from': accounts[2], 'value': prices[2]})
    tx.wait(1)
    # End offers Time 
    auction.closeOffers({"from": accounts[0]})
    # Reveal offers 
    tx = auction.revealOffer(secrets[1], prices[1], {'from':accounts[1]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[2], prices[2], {'from':accounts[2]})
    tx.wait(1)
    #Calculate Winner
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {'from':accounts[0]})
    tx.wait(1)
    # Winner claims asset
    tx = auction.winnerRetrivesToken({"from": accounts[2]})
    tx.wait(0)
    # Loser reinburses
    tx = auction.reiburseParticipant({"from": accounts[1]})
    tx.wait(0)
    # auctioneer gets payed
    tx = auction.ownerGetsPayed({"from": accounts[0]})
    tx.wait(0)
    # Si functiona pero no considera lo gastado en gas fees en todas las 
    # transaccione entonces se rompe pero en gral si jala todo. 
    assert(collectible.ownerOf(collectible_id) == accounts[2])
    assert(initial_balances[0] + prices[2] >= accounts[0].balance())
    assert(initial_balances[1] >= accounts[1].balance())
    assert(initial_balances[2] - prices[2] >= accounts[2].balance())

def test_integration_local():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    accounts = [get_account(),get_account(index=1),get_account(index=2)]
    secrets = ["S1", "S2", "S3"]
    prices = [Web3.toWei(0.01, 'ether'), Web3.toWei(0.11, 'ether'), Web3.toWei(0.12, 'ether')]
    initial_balances = [accounts[0].balance(), accounts[1].balance(), accounts[2].balance()]
    auction, initial_hash = deploy_auction()
    initial_auction_balance = auction.balance()
    collectible, collectible_id = last_nft()
    # Make ofers
    tx = auction.makeOffer(hashStrings(secrets[1], prices[1]), {'from': accounts[1], 'value': prices[1]})
    tx.wait(1)
    tx = auction.makeOffer(hashStrings(secrets[2], prices[2]), {'from': accounts[2], 'value': prices[2]})
    tx.wait(1)
    # End offers Time 
    auction.closeOffers({"from": accounts[0]})
    # Reveal offers 
    tx = auction.revealOffer(secrets[1], prices[1], {'from':accounts[1]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[2], prices[2], {'from':accounts[2]})
    tx.wait(1)
    #Calculate Winner
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {'from':accounts[0]})
    tx.wait(1)
    # Winner claims asset
    tx = auction.winnerRetrivesToken({"from": accounts[2]})
    tx.wait(0)
    # Loser reinburses
    tx = auction.reiburseParticipant({"from": accounts[1]})
    tx.wait(0)
    # auctioneer gets payed
    tx = auction.ownerGetsPayed({"from": accounts[0]})
    tx.wait(0)
    # Si functiona pero no considera lo gastado en gas fees en todas las 
    # transaccione entonces se rompe pero en gral si jala todo. 
    assert(collectible.ownerOf(collectible_id) == accounts[2])
    assert(initial_balances[0] + prices[2] == accounts[0].balance())
    assert(initial_balances[1] == accounts[1].balance())
    assert(initial_balances[2] - prices[2] == accounts[2].balance())

