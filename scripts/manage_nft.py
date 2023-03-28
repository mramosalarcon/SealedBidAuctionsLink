from brownie import CollectibleCreator, config, network
from scripts.helpful_scripts import get_account

OPENSEA_URL = " https://testnets.opensea.io/assets/{}/{}"
METADATA = "https://ipfs.io/ipfs/QmWb8W1n3MAbqT1QeSPVraXQ2mJrJDJjggmCjRJtXFBoDQ"


"""Deploys an ERC721 contract and mints an nft which is deposited into the first
    local account that ganache gives us. 
        
    Returns:
        collectible (contract): contract of the new NFT
        collectible_id (int): id of the collectible. 0 almost always, at least in this script. 

"""


def deploy_and_create_nft():
    account = get_account()
    collectible = CollectibleCreator.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    tx = collectible.createCollectible({"from": account})
    tx.wait(1)
    print("Collectible created!")
    collectible_id = collectible.tokenCounter() - 1
    print(
        f"Awesome!! You can view your NFT at {OPENSEA_URL.format(collectible.address, collectible_id)}"
    )
    return collectible, collectible_id


"""Creates an ERC721 token from the last deployed NFT contract. The mint 
    is deposited into the first local account given by ganace. 

    Returns:
        collectible (contract): contract of the new NFT
        collectible_id (int): id of the collectible.


"""


def create_nft():
    account = get_account()
    collectible = CollectibleCreator[-1]
    tx = collectible.createCollectible({"from": account})
    tx.wait(1)
    print("Collectible created!")
    collectible_id = collectible.tokenCounter() - 1
    print(
        f"Awesome!! You can view your NFT at {OPENSEA_URL.format(collectible.address, collectible_id)}"
    )
    return collectible, collectible_id


"""Returns the contract and id of the last token minted from the last 
    contract deployed. 


    Returns:
        collectible (contract): contract of the new NFT
        collectible_id (int): id of the collectible.

"""


def last_nft():
    collectible = CollectibleCreator[-1]
    return collectible, collectible.tokenCounter() - 1


def main():
    # deploy_and_create_nft()
    token_contract = CollectibleCreator.at(
        "0x7b4Bf48b219765392A839D6a47178A3633d412a0"
    )  # use the address where the contract is deployed
    CollectibleCreator.publish_source(token_contract)
