from brownie import CollectibleCreator, accounts, config, network, exceptions
from web3 import Web3
from scripts.helpful_scripts import  get_account, hashStrings

OPENSEA_URL =' https://testnets.opensea.io/assets/{}/{}'
METADATA = "https://ipfs.io/ipfs/QmR6xprTY253fDPM423C5t3EjdTVXuqPDXjPJhpp7v7gQc"

def deploy_and_create_nft():
    account = get_account()
    collectible = CollectibleCreator.deploy({"from": account}, publish_source = config["networks"][network.show_active()].get("verify", False))
    tx = collectible.createCollectible(METADATA, {"from": account})
    tx.wait(1)
    print("Collectible created!")
    collectible_id = collectible.tokenCounter() -1
    print(f"Awesome!! You can view your NFT at {OPENSEA_URL.format(collectible.address, collectible_id)}")
    return collectible, collectible_id

def create_nft():
    account = get_account()
    collectible = CollectibleCreator[-1]
    tx = collectible.createCollectible(METADATA, {"from": account})
    tx.wait(1)
    print("Collectible created!")
    collectible_id = collectible.tokenCounter() -1
    print(f"Awesome!! You can view your NFT at {OPENSEA_URL.format(collectible.address, collectible_id)}")
    return collectible, collectible_id

def last_nft():
    collectible = CollectibleCreator[-1]
    return collectible, collectible.tokenCounter() -1