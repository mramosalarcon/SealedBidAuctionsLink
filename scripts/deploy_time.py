from brownie import TimeOracle, config, network
from scripts.helpful_scripts import  get_account, TESTNETS

# Rinkeby
price_feeds = [
    '0x8A753747A1Fa494EC906cE90E9f37563A8AF630e',
    '0xCe3f7378aE409e1CE0dD6fFA70ab683326b73f04',
    '0xD4a33860578De61DBAbDc8BFdb98FD742fA7028e',
    '0x13E99C19833F557672B67C70508061A2E1e54162'
]

'''Deploys a time oracle in the testnets (rinkeby). Deployment does 
    not set the addresses from the priceffeds that will be used, those 
    are set via functions by the contract owner. 
        
    Returns:
        time_oracle (contract): Contract of the deployed oracle.

'''
def deploy_time():
    if network.show_active() not in TESTNETS:
        pass
    else:
        account = get_account()
        time_oracle = TimeOracle.deploy({"from": account}, 
            publish_source = config["networks"][network.show_active()].get("verify", False))
        return time_oracle

'''Gets the last deployed time oracle contract. 

    Returns:
        time_oracle (contract): Contract of the deployed oracle.

'''
def get_last_deployed_time():
    if len(TimeOracle) > 0:
        return TimeOracle[-1]

'''Deploys time contract and adds 4 pricefeeds. Takes the 4 pricefeed 
    oracles that have a 1hour or smaller heartbeat so the average time 
    between them is not more than an hour behind the real time.

    Returns:
        time_oracle (contract): Contract of the deployed oracle.

'''
def deploy_and_add_addresses():
    time_contract = deploy_time()
    account = get_account()
    # Agrega Feeds
    for feed in price_feeds:
        time_contract.addPriceFeed(feed, {"from": account})
    return time_contract

'''Lets you delete a priceFeed from the time oracle contract

   Args: id (int): id of the pricefeed in the list at the begginig
    of the contract

'''
def delete_feed(id = 2):
    account = get_account()
    time_contract = get_last_deployed_time()
    time_contract.deletePriceFeed(price_feeds[id], {"from": account})

'''Prints pricefeeds in the time oracle.

   Args: time_contract (contract)
        

'''
def print_data(time_contract):
    for i in range(time_contract.getLength()):
        print(time_contract.timeFeed(i))
    print(time_contract.getLatestTime())

def main():
    #time_contract = get_last_deployed_time()
    time_contract = deploy_and_add_addresses()

'''Lets you add a priceFeed to the time oracle contract

   Args: id (int): id of the pricefeed in the list at the begginig
    of the contract

'''
def add_one_feed(id = 1):
    account = get_account()
    time_contract = get_last_deployed_time()
    time_contract.addPriceFeed(price_feeds[id], {"from": account})





