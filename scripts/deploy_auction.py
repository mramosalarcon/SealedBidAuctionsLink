from brownie import SealedBidAuction, config, network
from web3 import Web3
from scripts.helpful_scripts import get_account, hashStrings
from scripts.manage_nft import deploy_and_create_nft, last_nft


"""Auction deployment funciton. First cereates an ERC721 contract, 
    mints a token and then proceeds to create an auction for that token. 

   Args: 
    min_price (uint): minimum price of the aution
    secret (string): The secret word to hash with the price.
    time (unix timestamp secodns, uint): Time when offers must close.
    time2 (unix timestamp secodns, uint): Time when reveals must close.
        
    Returns:

"""


def deploy_auction(
    min_price=Web3.to_wei(0.001, "ether"), secret="thisIsASecret", time=None, time2=None
):
    account = get_account(index=0)
    initialHash = hashStrings(secret, min_price)
    collectible, collectible_id = deploy_and_create_nft()
    if not time:
        time = 0
        time2 = 0
    auction = SealedBidAuction.deploy(
        initialHash,
        collectible,
        collectible_id,
        time,
        time2,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    tx = collectible.approve(auction, collectible_id, {"from": account})
    print(tx.timestamp)
    tx.wait(1)
    tx = auction.transferAssetToContract({"from": account})
    tx.wait(1)
    return auction, initialHash


"""Auction deployment funciton. Uses an already created NFT contract, 
    mints a token and then proceeds to create an auction for that token. 

   Args: 
    min_price (uint): minimum price of the aution
    secret (string): The secret word to hash with the price.
    time (unix timestamp secodns, uint): Time when offers must close.
    time2 (unix timestamp secodns, uint): Time when reveals must close.
        
    Returns:

"""


def deploy_auction_last_nft(
    min_price=Web3.to_wei(0.001, "ether"), secret="thisIsASecret", time=None, time2=None
):
    account = get_account(index=0)
    initialHash = hashStrings(secret, min_price)
    collectible, collectible_id = last_nft()
    if not time:
        time = 0
        time2 = 0
    auction = SealedBidAuction.deploy(
        initialHash,
        collectible,
        collectible_id,
        time,
        time2,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    return auction, initialHash


def main():
    deploy_auction_last_nft()
