from brownie import network, config, accounts, Contract, SealedBidAuction, CollectibleCreator
from scripts.helpful_scripts import  get_account, hashStrings
from web3 import Web3
from scripts.manage_nft import last_nft


MIN_PRICE = Web3.toWei(0.1, 'ether')
SECRET = "thisIsASecret"
METADATA = "https://ipfs.io/ipfs/QmR6xprTY253fDPM423C5t3EjdTVXuqPDXjPJhpp7v7gQc"

def main():
    gas_per_txn = []
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
    tx.wait(1)
    # Loser reinburses
    tx = auction.reiburseParticipant({"from": accounts[1]})
    tx.wait(1)
    # auctioneer gets payed
    tx = auction.ownerGetsPayed({"from": accounts[0]})
    tx.wait(1)


def deploy_auction(min_price = Web3.toWei(0.1, 'ether') , secret = "thisIsASecret"):
    account = get_account(index=0)
    initialHash = hashStrings(secret, min_price)
    collectible, collectible_id = deploy_and_create_nft()
    auction = SealedBidAuction.deploy(initialHash, collectible, collectible_id, {"from": account}, publish_source = config["networks"][network.show_active()].get("verify", False))
    tx = collectible.approve(auction, collectible_id, {"from": account})
    tx.wait(1)
    tx = auction.transferAssetToContract({"from": account})
    tx.wait(1)
    return auction, initialHash

def deploy_and_create_nft():
    account = get_account()
    collectible = CollectibleCreator.deploy({"from": account}, publish_source = config["networks"][network.show_active()].get("verify", False))
    #print(f"Gas in NFT contract creation {collectible.gas_used}")
    tx = collectible.createCollectible(METADATA, {"from": account})
    tx.wait(1)
    collectible_id = collectible.tokenCounter() -1
    return collectible, collectible_id