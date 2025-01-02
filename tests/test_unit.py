from brownie import SealedBidAuction, accounts, config, network, exceptions
from web3 import Web3
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    hashStrings,
    time_now,
)
from scripts.deploy_auction import deploy_auction
from scripts.manage_nft import last_nft
from scripts.deploy_factory import deploy_factory, deploy_auction_from_factory
import pytest
import time

MIN_PRICE = Web3.to_wei(0.001, "ether")
SECRET = "thisIsASecret"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


"""
THE FOLLOWING TESTS DO NOT TAKE INTO ACCOUNT TIMES, OFFER AND REVEAL TIMES ARE SET 
TO A PAST DATE, FOR NOW WE WILL ONLY TEST THE OVERALL FUNCTIONALLITY. TIME
DEPENDENT TEST WILL EVENTUALLY COME ALONG. 
"""

"""
Test that the deployment of the contract is actually made and that
it initializes as intended.
"""


def test_deploy():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    auction, hash = deploy_auction(MIN_PRICE, SECRET)
    # Act
    collectible, collectible_id = last_nft()
    # Assert
    assert auction.auction_state() == 1
    assert collectible.ownerOf(collectible_id) == auction
    assert str(auction.minimumPriceHash()) == hash.hex()
    assert auction.owner() == get_account()


"""
Verifies that the owner can't place an offer for his own auction.
"""


def test_owner_cant_participate():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    price = Web3.to_wei(0.15, "ether")
    secret = "Secret1"
    auction, hash = deploy_auction(MIN_PRICE, SECRET)
    with pytest.raises(exceptions.VirtualMachineError):
        auction.makeOffer(hashStrings(secret, price), {"from": account, "value": price})


"""
Checks that an offer reverts if the value in the transaction is 0.
"""


def test_min_amount_transfer():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    price = Web3.to_wei(0, "ether")
    secret = "Secret1"
    auction, hash = deploy_auction(MIN_PRICE, SECRET)
    with pytest.raises(exceptions.VirtualMachineError):
        auction.makeOffer(hashStrings(secret, price), {"from": account, "value": price})


"""
Checks that an offer is actually made and stored in the contract
"""


def test_make_offer():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    auction, hash = deploy_auction(MIN_PRICE, SECRET)
    price = Web3.to_wei(0.16, "ether")
    secret = "Secret1"
    tx = auction.makeOffer(
        hashStrings(secret, price), {"from": account, "value": price}
    )
    tx.wait(1)
    assert auction.accountToAmount(account) == price
    assert str(auction.accountToHash(account)) == hashStrings(secret, price).hex()
    assert auction.players(0) == account


"""
Makes sure that no single wallet can make more than one offer
"""


def test_no_double_bids():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    price = Web3.to_wei(0.15, "ether")
    secret = "Secret1"
    auction, hash = deploy_auction(MIN_PRICE, SECRET)
    tx = auction.makeOffer(
        hashStrings(secret, price), {"from": account, "value": price}
    )
    tx.wait(1)
    price = Web3.to_wei(0.13, "ether")
    secret = "Secret2"
    with pytest.raises(exceptions.VirtualMachineError):
        auction.makeOffer(hashStrings(secret, price), {"from": account, "value": price})


"""
Checks that the owner of the contrat can end the bidding period and move
the auction state to the offer reveal period.
"""


def test_close_bids_by_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    auction, hash = deploy_auction()
    tx = auction.nextPhase({"from": account})
    tx.wait(1)
    assert auction.auction_state() == 2


"""
Checks that the contract owner cant just skip the offer period and go straight 
to revealing the minimum prize. 
"""


def test_skip_reveal():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    auction, hash = deploy_auction()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": account})
        tx.wait(1)


"""
Makes sure no offers can be revealed in the wrong auction state. 
"""


def test_reveal_offer_wrong_time():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    auction, hash = deploy_auction()
    price = Web3.to_wei(0.16, "ether")
    secret = "Secret1"
    tx = auction.makeOffer(
        hashStrings(secret, price), {"from": account, "value": price}
    )
    tx.wait(1)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.revealOffer(bytes(secret, "utf-8"), price, {"from": account})
        tx.wait(1)


"""
Chacks that that wallets cant reveal offers if they did not make one 
in the first place. 
"""


def test_reveal_offer_not_participant():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    auction, hash = deploy_auction()
    tx = auction.nextPhase({"from": get_account()})
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.revealOffer(
            bytes("secret", "utf-8"), Web3.to_wei(0.16, "ether"), {"from": account}
        )
        tx.wait(1)


"""
Tests that the solidity hash matches the hash calculated outside solidity given 
te same amount and secrets. 
"""


def test_encoding_matches():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    auction, hash = deploy_auction()
    price = Web3.to_wei(0.16, "ether")
    secret = "Secret1"
    tx = auction.makeOffer(
        hashStrings(secret, price), {"from": account, "value": price}
    )
    tx.wait(1)
    print(auction.accountToHash(account))
    tx = auction.nextPhase({"from": get_account()})
    tx.wait(1)
    tx = auction.revealOffer(secret, price, {"from": account})
    tx.wait(1)
    assert auction.accountToOffer(account) == price


"""
Shows that offers cant be reveales twice.
"""


def test_cant_reveal_twice():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    auction, hash = deploy_auction()
    price = Web3.to_wei(0.16, "ether")
    secret = "Secret1"
    tx = auction.makeOffer(
        hashStrings(secret, price), {"from": account, "value": price}
    )
    tx.wait(1)
    tx = auction.nextPhase({"from": get_account()})
    tx.wait(1)
    tx = auction.revealOffer(secret, price, {"from": account})
    tx.wait(1)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.revealOffer(secret, price, {"from": account})
        tx.wait(1)


"""
In case no wallet meets the minimun prize then the acution assignes no winner.
"""


def test_no_winner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    accounts = [get_account(index=1), get_account(index=2), get_account(index=3)]
    auction, hash = deploy_auction()
    secrets = ["S1", "S2", "S3"]
    prices = [
        Web3.to_wei(0.00001, "ether"),
        Web3.to_wei(0.00004, "ether"),
        Web3.to_wei(0.00005, "ether"),
    ]
    tx = auction.makeOffer(
        hashStrings(secrets[0], prices[0]), {"from": accounts[0], "value": prices[0]}
    )
    tx.wait(1)
    tx = auction.makeOffer(
        hashStrings(secrets[1], prices[1]), {"from": accounts[1], "value": prices[1]}
    )
    tx.wait(1)
    tx = auction.makeOffer(
        hashStrings(secrets[2], prices[2]), {"from": accounts[2], "value": prices[2]}
    )
    tx.wait(1)
    tx = auction.nextPhase({"from": get_account()})
    tx.wait(1)
    tx = auction.revealOffer(secrets[0], prices[0], {"from": accounts[0]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[1], prices[1], {"from": accounts[1]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[2], prices[2], {"from": accounts[2]})
    tx.wait(1)
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": get_account()})
    tx.wait(1)
    # tx = auction.nextPhase({'from':get_account()})
    # tx.wait(1)
    assert auction.winner() == "0x0000000000000000000000000000000000000000"
    assert auction.amount() == 0
    assert auction.auction_state() == 4
    return auction, accounts, prices


"""
Verifies that in case no one wins the auctioneer can get the NFT back.
"""


def test_give_token_back():
    auction, accounts, prices = test_no_winner()
    collectible, collectible_id = last_nft()
    assert collectible.ownerOf(collectible_id) == auction
    assert auction.owner_claim() == 0
    tx = auction.ownerGetsPayed({"from": get_account()})
    tx.wait(1)
    assert collectible.ownerOf(collectible_id) == get_account()
    assert auction.owner_claim() == 1
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.ownerGetsPayed({"from": get_account()})
        tx.wait(1)


"""
In case there is no winner, tha contract gives back the deposits the 
right way. 
"""


def test_deposit_back():
    auction, accounts, prices = test_no_winner()
    prices = [
        Web3.to_wei(0.00001, "ether"),
        Web3.to_wei(0.00004, "ether"),
        Web3.to_wei(0.00005, "ether"),
    ]
    initialBalance = accounts[0].balance()
    tx = auction.reimburseParticipant({"from": accounts[0]})
    tx.wait(1)
    assert initialBalance == accounts[0].balance() - prices[0]


"""
Checks if the auction winner, given that there is one, is chosen correctly.
"""


def test_chooses_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    accounts = [get_account(index=1), get_account(index=2), get_account(index=3)]
    auction, hash = deploy_auction()
    secrets = ["S1", "S2", "S3"]
    prices = [
        Web3.to_wei(0.16, "ether"),
        Web3.to_wei(0.50, "ether"),
        Web3.to_wei(0.21, "ether"),
    ]
    tx = auction.makeOffer(
        hashStrings(secrets[0], prices[0]), {"from": accounts[0], "value": prices[0]}
    )
    tx.wait(1)
    tx = auction.makeOffer(
        hashStrings(secrets[1], prices[1]), {"from": accounts[1], "value": prices[1]}
    )
    tx.wait(1)
    tx = auction.makeOffer(
        hashStrings(secrets[2], prices[2]), {"from": accounts[2], "value": prices[2]}
    )
    tx.wait(1)
    tx = auction.nextPhase({"from": get_account()})
    tx.wait(1)
    tx = auction.revealOffer(secrets[0], prices[0], {"from": accounts[0]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[1], prices[1], {"from": accounts[1]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[2], prices[2], {"from": accounts[2]})
    tx.wait(1)
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": get_account()})
    tx.wait(1)
    # tx = auction.nextPhase({'from':get_account()})
    # tx.wait(1)
    assert auction.winner() == accounts[1]
    assert auction.amount() == prices[1]
    assert auction.auction_state() == 4
    return auction, accounts, prices


"""
If there is only one bidder and he does not reveal then there is no winner check.
"""


def test_chooses_winner_correctly_no_reveals():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    accounts = [get_account(index=1), get_account(index=2), get_account(index=3)]
    auction, hash = deploy_auction()
    secrets = ["S1", "S2", "S3"]
    prices = [
        Web3.to_wei(0.16, "ether"),
        Web3.to_wei(0.50, "ether"),
        Web3.to_wei(0.21, "ether"),
    ]
    tx = auction.makeOffer(
        hashStrings(secrets[0], prices[0]), {"from": accounts[0], "value": prices[0]}
    )
    tx.wait(1)
    tx = auction.makeOffer(
        hashStrings(secrets[1], prices[1]), {"from": accounts[1], "value": prices[1]}
    )
    tx.wait(1)
    tx = auction.nextPhase({"from": get_account()})
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": get_account()})
    tx.wait(1)
    # tx = auction.nextPhase({'from':get_account()})
    # tx.wait(1)
    assert auction.winner() == ZERO_ADDRESS
    assert auction.amount() == 0
    assert auction.auction_state() == 4
    return auction, accounts, prices


"""
Checks that the auctions countinues and chooses a winner even if not all 
offers were revealed. Which might happen and e cant wait for all participants 
to reveal, they might forget, loose thair keys, ...
"""


def test_participant_no_reveal():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    accounts = [get_account(index=1), get_account(index=2), get_account(index=3)]
    auction, hash = deploy_auction()
    secrets = ["S1", "S2", "S3"]
    prices = [
        Web3.to_wei(0.16, "ether"),
        Web3.to_wei(0.50, "ether"),
        Web3.to_wei(0.21, "ether"),
    ]
    tx = auction.makeOffer(
        hashStrings(secrets[0], prices[0]), {"from": accounts[0], "value": prices[0]}
    )
    tx.wait(1)
    tx = auction.makeOffer(
        hashStrings(secrets[1], prices[1]), {"from": accounts[1], "value": prices[1]}
    )
    tx.wait(1)
    tx = auction.makeOffer(
        hashStrings(secrets[2], prices[2]), {"from": accounts[2], "value": prices[2]}
    )
    tx.wait(1)
    tx = auction.nextPhase({"from": get_account()})
    tx.wait(1)
    tx = auction.revealOffer(secrets[1], prices[1], {"from": accounts[1]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[2], prices[2], {"from": accounts[2]})
    tx.wait(1)
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": get_account()})
    tx.wait(1)
    # tx = auction.nextPhase({'from':get_account()})
    # tx.wait(1)
    assert auction.winner() == accounts[1]
    assert auction.amount() == prices[1]
    assert auction.auction_state() == 4
    return auction, accounts, prices


"""
Checks that if the NFT was sold to the largest bidder then the ex-owner of the 
token and creator of the acution can get the amount of eth that won. 
"""


def test_auctioneer_gets_payed():
    account = get_account()
    auction, accounts, prices = test_chooses_winner_correctly()
    auction_initial_balance = auction.balance()
    account_initial_balance = account.balance()
    amount_sold_for = auction.amount()
    assert auction.owner_claim() == 0
    tx = auction.ownerGetsPayed({"from": account})
    assert auction.owner_claim() == 1
    tx.wait(1)
    assert account_initial_balance + amount_sold_for == account.balance()
    assert auction.balance() == auction_initial_balance - amount_sold_for
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.ownerGetsPayed({"from": get_account()})
        tx.wait(1)
    return auction, accounts, prices


"""
In case a participant does not reveal, the test checks if the owner 
can still get payed. 
"""


def test_auctioneer_gets_payed_no_reveal():
    account = get_account()
    auction, accounts, prices = test_participant_no_reveal()
    auction_initial_balance = auction.balance()
    account_initial_balance = account.balance()
    amount_sold_for = auction.amount()
    tx = auction.ownerGetsPayed({"from": account})
    tx.wait(1)
    assert account_initial_balance + amount_sold_for == account.balance()
    assert auction.balance() == auction_initial_balance - amount_sold_for
    return auction, accounts, prices


"""
Tests that the accounts thad made an offer and did not reveal it can still 
claim back the eth they deposited once the auction ends. 
"""


def test_reimbursements_no_reveal():
    auction, accounts, prices = test_auctioneer_gets_payed_no_reveal()
    auction_initial_balance = auction.balance()
    accounts_initial_balances = [
        accounts[0].balance(),
        accounts[1].balance(),
        accounts[2].balance(),
    ]
    tx = auction.reimburseParticipant({"from": accounts[0]})
    tx.wait(1)
    tx = auction.reimburseParticipant({"from": accounts[2]})
    tx.wait(1)
    assert accounts_initial_balances[0] + prices[0] == accounts[0].balance()
    assert accounts_initial_balances[2] + prices[2] == accounts[2].balance()
    assert auction_initial_balance - prices[0] - prices[2] == auction.balance()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.reimburseParticipant({"from": accounts[1]})
        tx.wait(1)
    return auction, accounts


"""
Checks that reinbursements are made to the accounts that did not win the auction.
"""


def test_reimbursements():
    auction, accounts, prices = test_auctioneer_gets_payed()
    auction_initial_balance = auction.balance()
    accounts_initial_balances = [
        accounts[0].balance(),
        accounts[1].balance(),
        accounts[2].balance(),
    ]
    tx = auction.reimburseParticipant({"from": accounts[0]})
    tx.wait(1)
    tx = auction.reimburseParticipant({"from": accounts[2]})
    tx.wait(1)
    assert accounts_initial_balances[0] + prices[0] == accounts[0].balance()
    assert accounts_initial_balances[2] + prices[2] == accounts[2].balance()
    assert auction_initial_balance - prices[0] - prices[2] == auction.balance()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.reimburseParticipant({"from": accounts[1]})
        tx.wait(1)
    return auction, accounts


"""
Verifies that an account cant get reinbursed twice.
"""


def test_double_reinbursements():
    auction, accounts = test_reimbursements()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.reimburseParticipant({"from": accounts[0]})
        tx.wait(1)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.reimburseParticipant({"from": accounts[2]})
        tx.wait(1)


"""
In case the auction winner deposited 1 eth but offered 0.1 then he needs to 
get the 0.9 back. That is what this test checks, but with different numbers.  
"""


def test_winner_gives_more_than_offered():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    accounts = [get_account(index=1), get_account(index=2)]
    auction, hash = deploy_auction()
    secrets = ["S1", "S2"]
    prices = [Web3.to_wei(0.1, "ether"), Web3.to_wei(0.1, "ether")]
    tx = auction.makeOffer(
        hashStrings(secrets[0], prices[0]),
        {"from": accounts[0], "value": Web3.to_wei(0.5, "ether")},
    )
    tx.wait(1)
    tx = auction.nextPhase({"from": get_account()})
    tx.wait(1)
    tx = auction.revealOffer(secrets[0], prices[0], {"from": accounts[0]})
    tx.wait(1)
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": get_account()})
    tx.wait(1)
    # tx = auction.nextPhase({'from':get_account()})
    # tx.wait(1)
    contract_balance = auction.balance()
    participant_balance = accounts[0].balance()
    assert auction.accountToAmount(accounts[0]) == Web3.to_wei(0.4, "ether")
    tx = auction.reimburseParticipant({"from": accounts[0]})
    tx.wait(1)
    assert contract_balance - auction.accountToOffer(accounts[0]) == Web3.to_wei(
        0.4, "ether"
    )
    assert participant_balance + Web3.to_wei(0.4, "ether") == accounts[0].balance()
    assert auction.accountToAmount(accounts[0]) == 0
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.reimburseParticipant({"from": accounts[0]})
        tx.wait(1)


"""
Checks that the auction winner retrive the NFT from the contract. 
"""


def test_winner_retrives_token():
    auction, accounts, prices = test_chooses_winner_correctly()
    collectible, collectible_id = last_nft()
    assert collectible.ownerOf(collectible_id) == auction
    tx = auction.winnerRetrivesToken({"from": accounts[1]})
    tx.wait(1)
    assert collectible.ownerOf(collectible_id) == accounts[1]


def test_non_winner_retrives_token():
    auction, accounts, prices = test_chooses_winner_correctly()
    collectible, collectible_id = last_nft()
    assert collectible.ownerOf(collectible_id) == auction
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.winnerRetrivesToken({"from": accounts[0]})
        tx.wait(1)
    assert collectible.ownerOf(collectible_id) == auction


"""
NOW, THE TESTS THAT CHECK THE SET TIMES ARE ACTUELLY WORKING.
"""
## Tests con tiempos en cuenta

"""
Tests that the times deployed in the contract are right. 
"""


def test_right_times_deploy():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    time1 = time_now() + 5
    time2 = time1 + 10
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    # Act
    collectible, collectible_id = last_nft()
    # Assert
    assert auction.auction_state() == 1
    assert collectible.ownerOf(collectible_id) == auction
    assert str(auction.minimumPriceHash()) == hash.hex()
    assert auction.owner() == get_account()
    assert auction.revealTime() == time1
    assert auction.winnerTime() == time2


"""
Tests that the auctioneer can't close offers before the time he set 
passes
"""


def test_cant_close_offers_on_wrong_time_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    account = get_account()
    time1 = time_now() + 50
    time2 = time1 + 100
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    # Act
    collectible, collectible_id = last_nft()
    # Assert
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.nextPhase({"from": account})
        tx.wait(1)
    return account, auction


"""
Tests that no other account can close offers when the time is not right
"""


def test_cant_close_offers_on_wrong_time():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    account2 = get_account(index=1)
    time1 = time_now() + 50
    time2 = time1 + 100
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    # Assert
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.nextPhase({"from": account2})
        tx.wait(1)
    return account2, auction


"""
Test that close offers can bu run in the right time. 
"""


def test_close_offers_right_time():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    account = get_account(index=2)
    time1 = time_now()
    time2 = time1 + 10
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    # Act
    time.sleep(5)
    # Assert
    tx = auction.nextPhase({"from": account})
    tx.wait(1)
    assert auction.auction_state() == 2
    return account, auction


"""
Owner can close offers in the right time. 
"""


def test_close_offers_right_time_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    account = get_account()
    time1 = time_now()
    time2 = time1 + 10
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    # Act
    time.sleep(5)
    # Assert
    tx = auction.nextPhase({"from": account})
    tx.wait(1)
    assert auction.auction_state() == 2
    return account, auction


"""
No reveals colsing before set time + x seconds, in testing i hardoded that 
time differential to 5. This gives the owner an opportunity to reveal the 
minimum price he sets but that time is not infinite. If the auctioneer 
forgets the amount or the secret and this time difference was not imlemented 
then the auction would be stuck there forever. 
"""


def test_close_reveals_wrong_time():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.nextPhase({"from": account})
        tx.wait(1)


"""
Owner cant close reveals when it is not time to.
"""


def test_close_reveals_wrong_time_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time_owner()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": account})
        tx.wait(1)


"""
There are 2 methods for closing reveals, one for the owner an one for the 
keeper. Checks that they cant fun the one they sould not. 
"""


def test_close_reveals_wrong_method():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time()
    time.sleep(5)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": account})
        tx.wait(1)


"""
Same as last but for the owner
"""


def test_close_reveals_wrong_method_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time()
    # Act
    time.sleep(5)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.nextPhase({"from": account})
        tx.wait(1)


"""
Test reveals can be closed at the right time and with the right method. 
"""


def test_close_reveals_right_time_and_method():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time()
    time.sleep(43)
    tx = auction.nextPhase({"from": account})
    tx.wait(1)
    assert auction.auction_state() == 4


"""
Tests that the time difference is actually working
"""


def test_close_reveals_right_time_and_method_with_diffrence():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time()
    time.sleep(1)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.nextPhase({"from": account})
        tx.wait(1)


"""
Test reveals can be closed at the right time and with the right method. For the 
owner of the auciton.
"""


def test_close_reveals_right_time_and_method_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time_owner()
    time.sleep(5)
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": account})
    tx.wait(1)
    assert auction.auction_state() == 4


"""
Tests that offers cant be revealed by owner in the wrong time. 
"""


def test_close_reveals_right_time_and_method_with_diffrence_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time_owner()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": account})
        tx.wait(1)


"""
Tests that the winner is chosen correctly when the closing is dome by the owner
"""


def test_winner_with_colse_by_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account1 = get_account()
    account2 = get_account(index=1)
    time1 = time_now()
    time2 = time1 + 10
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    secrets = ["S1", "S2"]
    prices = [Web3.to_wei(0.1, "ether"), Web3.to_wei(0.1, "ether")]
    tx = auction.makeOffer(
        hashStrings(secrets[0], prices[0]),
        {"from": account2, "value": Web3.to_wei(0.1, "ether")},
    )
    tx.wait(1)
    tx = auction.nextPhase({"from": account2})
    tx.wait(1)
    tx = auction.revealOffer(secrets[0], prices[0], {"from": account2})
    tx.wait(1)
    time.sleep(10)
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": account1})
    tx.wait(1)
    assert auction.winner() == account2
    assert auction.amount() == Web3.to_wei(0.1, "ether")
    assert auction.minimumPrice() != 0


"""
Tests that the winner is chosen correctly when the closing is done by 
someone else and the minimum price stays at 0. 
"""


def test_winner_with_colse_by_x():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account1 = get_account()
    account2 = get_account(index=1)
    time1 = time_now()
    time2 = time1 + 10
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    secrets = ["S1", "S2"]
    prices = [Web3.to_wei(0.1, "ether"), Web3.to_wei(0.1, "ether")]
    tx = auction.makeOffer(
        hashStrings(secrets[0], prices[0]),
        {"from": account2, "value": Web3.to_wei(0.1, "ether")},
    )
    tx.wait(1)
    tx = auction.nextPhase({"from": account2})
    tx.wait(1)
    tx = auction.revealOffer(secrets[0], prices[0], {"from": account2})
    tx.wait(1)
    time.sleep(46)
    tx = auction.nextPhase({"from": account2})
    tx.wait(1)
    assert auction.winner() == account2
    assert auction.amount() == Web3.to_wei(0.1, "ether")
    assert auction.minimumPrice() == 0


"""
Cheks that the auction is colse and no winner is chosen in case 
not one offer reaches the minimum price set by the owner. All when 
the auction is closed by the owner.
"""


def test_winner_with_colse_by_owner_bad_min_price():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account1 = get_account()
    account2 = get_account(index=1)
    time1 = time_now()
    time2 = time1 + 10
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    secrets = ["S1", "S2"]
    prices = [Web3.to_wei(0.00009, "ether"), Web3.to_wei(0.00009, "ether")]
    tx = auction.makeOffer(
        hashStrings(secrets[0], prices[0]),
        {"from": account2, "value": Web3.to_wei(0.3, "ether")},
    )
    tx.wait(1)
    tx = auction.nextPhase({"from": account2})
    tx.wait(1)
    tx = auction.revealOffer(secrets[0], prices[0], {"from": account2})
    tx.wait(1)
    time.sleep(10)
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": account1})
    tx.wait(1)
    assert auction.winner() == ZERO_ADDRESS
    assert auction.amount() == 0
    assert auction.minimumPrice() != 0


"""
Same as last but with the auction being closed by another account. 
"""


def test_winner_with_colse_by_x_bad_min_price():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account1 = get_account()
    account2 = get_account(index=1)
    time1 = time_now()
    time2 = time1 + 10
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    secrets = ["S1", "S2"]
    prices = [Web3.to_wei(0.09, "ether"), Web3.to_wei(0.09, "ether")]
    tx = auction.makeOffer(
        hashStrings(secrets[0], prices[0]),
        {"from": account2, "value": Web3.to_wei(0.2, "ether")},
    )
    tx.wait(1)
    tx = auction.nextPhase({"from": account2})
    tx.wait(1)
    tx = auction.revealOffer(secrets[0], prices[0], {"from": account2})
    tx.wait(1)
    time.sleep(46)
    tx = auction.nextPhase({"from": account2})
    tx.wait(1)
    assert auction.winner() == account2
    assert auction.amount() == prices[0]
    assert auction.minimumPrice() == 0


"""
Verifies that factory address is setup when deploying from there, if auction not deployed 
from factory then address is set to the deployer.
"""


def test_factory_variable_is_setup():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    factory = deploy_factory()
    auction, initialHash = deploy_auction_from_factory()
    assert auction.factory() == factory.address


"""
Revises that the factory gets a commision once an auction is over
"""


def test_factory_gets_comission():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    factory = deploy_factory()
    auction, initialHash = deploy_auction_from_factory()
    accounts = [get_account(), get_account(index=1), get_account(index=2)]
    secrets = ["S1", "S2", "S3"]
    prices = [
        Web3.to_wei(0.01, "ether"),
        Web3.to_wei(0.11, "ether"),
        Web3.to_wei(0.12, "ether"),
    ]
    initial_balances = [
        accounts[0].balance(),
        accounts[1].balance(),
        accounts[2].balance(),
    ]
    # Make ofers
    tx = auction.makeOffer(
        hashStrings(secrets[1], prices[1]), {"from": accounts[1], "value": prices[1]}
    )
    tx.wait(1)
    tx = auction.makeOffer(
        hashStrings(secrets[2], prices[2]), {"from": accounts[2], "value": prices[2]}
    )
    tx.wait(1)
    # End offers Time
    auction.nextPhase({"from": accounts[0]})
    # Reveal offers
    tx = auction.revealOffer(secrets[1], prices[1], {"from": accounts[1]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[2], prices[2], {"from": accounts[2]})
    tx.wait(1)
    # Calculate Winner
    print(auction.factory())
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": accounts[0]})
    tx.wait(1)
    # auctioneer gets payed
    tx = auction.ownerGetsPayed({"from": accounts[0]})
    tx.wait(0)
    assert factory.balance() > 0
    assert initial_balances[0] + Web3.to_wei(0.12, "ether") > accounts[0].balance()
    return factory


"""
Makes sure the factory owner can withdray funds from the factory. 
"""


def test_factory_owner_can_retrive_funds():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    factory = test_factory_gets_comission()
    account = get_account()
    account_balance = account.balance()
    assert factory.balance() > 0
    tx = factory.transferFunds(account.address, {"from": account})
    tx.wait(1)
    assert account_balance < account.balance()
    assert factory.balance() == 0
