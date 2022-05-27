from brownie import AuctionFactory, SealedBidAuction, Contract, config, network
from web3 import Web3
from scripts.helpful_scripts import  get_account, hashStrings,time_now
from scripts.manage_nft import deploy_and_create_nft, create_nft
import time

N = 10

'''Deploys a contract factory for auctoins. 
        
    Returns:
        factory (contract): Factory contract address. 

'''

def deploy_factory(min_price = Web3.toWei(0.1, 'ether') , secret = "thisIsASecret"):
    account = get_account(index=0)
    factory = AuctionFactory.deploy({"from": account}, publish_source = config["networks"][network.show_active()].get("verify", False))
    return factory


'''Deploys a an auction from de last factory deployed in the network. If 
    times are not specified then sets them to 0, This helps to test the 
    overall logic without the time constraints. 

    Args:
        min_price (uint): minimum price of the aution
        secret (string): The secret word to hash with the price.
        time1 (unix timestamp secodns, uint): Time when offers must close.
        time2 (unix timestamp secodns, uint): Time when reveals must close.
        
    Returns:
        auction (contract): Contract of the deployed auction in the factory.
        initialHash (bytes): hash of the minPrice and secret. 

'''

def deploy_auction_from_factory(min_price = Web3.toWei(0.1, 'ether') , secret = "thisIsASecret", time1=None, time2=None):
    account = get_account()
    initialHash = hashStrings(secret, min_price)
    factory = AuctionFactory[-1]
    #collectible, collectible_id = create_nft()
    collectible, collectible_id = deploy_and_create_nft()
    if not time1:
        time1 = 0
        time2 = 0
    collectible, collectible_id = create_nft()
    tx = factory.createSealedBidAuctionContract(initialHash, collectible, collectible_id, time1 , time2, {"from": account})
    tx.wait(1)
    auction_address = factory.sealedBidAuctionArrayContracts(0)
    #print(auction_address)
    auction = Contract.from_abi( SealedBidAuction._name, auction_address, SealedBidAuction.abi)
    tx = collectible.approve(auction, collectible_id, {"from": account})
    tx.wait(1)
    tx = auction.transferAssetToContract({"from": account})
    tx.wait(1)
    return auction, initialHash

'''Deploys N auctions, then preforms upkeep and prints if upkeep should have been preformed. 

    Args:
        min_price (uint): minimum price of the aution
        secret (string): The secret word to hash with the price.
        time1 (unix timestamp secodns, uint): Time when offers must close.
        time2 (unix timestamp secodns, uint): Time when reveals must close.
        
    Returns:
        The emits of each iteration. 

'''
def deploy_n_auctions_from_factory(min_price = Web3.toWei(0.1, 'ether') , secret = "thisIsASecret", time1=None, time2=None):
    deploy_factory()
    deploy_auction_from_factory(time1=time_now(), time2=time_now())
    #time.sleep(5)
    #for j in range(10):
    #    print(factory.checkKeep("a"))
    #    if(factory.checkKeep("a")):
    #        tx = factory.performUpkeep("a")
    #        tx.wait(1)
            #print(tx.info())
    #    time.sleep(5)
    


def main():
    #deploy_factory()
    deploy_n_auctions_from_factory()
    #deploy_factory_and_create_acution()
    #deploy_auction_from_factory()