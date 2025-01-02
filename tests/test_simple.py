import pytest
from brownie import SimpleNFT, accounts, exceptions
from web3 import Web3

@pytest.fixture
def nft_contract():
    # Deploy the contract using the first account as the owner
    owner = accounts[0]
    contract = SimpleNFT.deploy({"from": owner})
    return contract

def test_deployment(nft_contract):
    """Test contract deployment and initial state"""
    # Check contract owner
    assert nft_contract.owner() == accounts[0]
    # Check token name and symbol
    assert nft_contract.name() == "SimpleNFT"
    assert nft_contract.symbol() == "SNFT"

def test_minting(nft_contract):
    """Test NFT minting functionality"""
    owner = accounts[0]
    recipient = accounts[1]
    
    # Test successful minting
    tx = nft_contract.mintNFT(recipient, {"from": owner})
    tx.wait(1)
    
    # Verify token ownership and balance
    assert nft_contract.ownerOf(1) == recipient
    assert nft_contract.balanceOf(recipient) == 1
    
    # Verify event emission
    assert len(tx.events) == 1
    assert tx.events["Transfer"]["from"] == "0x0000000000000000000000000000000000000000"
    assert tx.events["Transfer"]["to"] == recipient
    assert tx.events["Transfer"]["tokenId"] == 1

def test_minting_unauthorized(nft_contract):
    """Test minting restrictions"""
    unauthorized_user = accounts[1]
    recipient = accounts[2]
    
    # Test minting from unauthorized account
    with pytest.raises(exceptions.VirtualMachineError):
        nft_contract.mintNFT(recipient, {"from": unauthorized_user})

def test_transfer(nft_contract):
    """Test NFT transfer functionality"""
    owner = accounts[0]
    sender = accounts[1]
    recipient = accounts[2]
    
    # Mint token to sender
    nft_contract.mintNFT(sender, {"from": owner})
    
    # Test successful transfer
    tx = nft_contract.transferNFT(sender, recipient, 1, {"from": sender})
    tx.wait(1)
    
    assert tx.events["Transfer"]["from"] == sender
    assert tx.events["Transfer"]["to"] == recipient
    assert tx.events["Transfer"]["tokenId"] == 1
    
    
    # Verify new ownership and balances
    assert nft_contract.ownerOf(1) == recipient
    assert nft_contract.balanceOf(sender) == 0
    assert nft_contract.balanceOf(recipient) == 1
    

# def test_transfer_unauthorized(nft_contract):
#     """Test transfer restrictions"""
#     owner = accounts[0]
#     token_owner = accounts[1]
#     unauthorized_user = accounts[2]
#     recipient = accounts[3]
    
#     # Mint token to token_owner
#     nft_contract.mintNFT(token_owner, {"from": owner})
    
#     # Test transfer from unauthorized account
#     with pytest.raises(exceptions.VirtualMachineError):
#         nft_contract.transferNFT(
#             token_owner, 
#             recipient, 
#             1, 
#             {"from": unauthorized_user}
#         )

def test_approved_transfer(nft_contract):
    """Test transfer with approval"""
    owner = accounts[0]
    token_owner = accounts[1]
    approved_user = accounts[2]
    recipient = accounts[3]
    
    # Mint token to token_owner
    nft_contract.mintNFT(token_owner, {"from": owner})
    
    # Approve another address to transfer the token
    nft_contract.approve(approved_user, 1, {"from": token_owner})
    
    # Test transfer from approved account
    tx = nft_contract.transferNFT(
        token_owner, 
        recipient, 
        1, 
        {"from": approved_user}
    )
    tx.wait(1)
    
    assert nft_contract.ownerOf(1) == recipient

# def test_transfer_to_zero_address(nft_contract):
#     """Test transfer to zero address"""
#     owner = accounts[0]
#     sender = accounts[1]
#     zero_address = "0x0000000000000000000000000000000000000000"
    
#     # Mint token to sender
#     nft_contract.mintNFT(sender, {"from": owner})
    
#     # Test transfer to zero address
#     with pytest.raises(exceptions.VirtualMachineError):
#         nft_contract.transferNFT(
#             sender, 
#             zero_address, 
#             1, 
#             {"from": sender}
#         )

# def test_non_existent_token(nft_contract):
#     """Test operations with non-existent tokens"""
#     sender = accounts[1]
#     recipient = accounts[2]
#     non_existent_token_id = 999
    
#     # Test transfer of non-existent token
#     with pytest.raises(exceptions.VirtualMachineError):
#         nft_contract.transferNFT(
#             sender, 
#             recipient, 
#             non_existent_token_id, 
#             {"from": sender}
#         )

def test_multiple_transfers(nft_contract):
    """Test multiple transfers of the same token"""
    owner = accounts[0]
    user1 = accounts[1]
    user2 = accounts[2]
    user3 = accounts[3]
    
    # Mint token
    nft_contract.mintNFT(user1, {"from": owner})
    
    # Perform multiple transfers
    nft_contract.transferNFT(user1, user2, 1, {"from": user1})
    assert nft_contract.ownerOf(1) == user2
    
    nft_contract.transferNFT(user2, user3, 1, {"from": user2})
    assert nft_contract.ownerOf(1) == user3
    
    # Verify final balances
    assert nft_contract.balanceOf(user1) == 0
    assert nft_contract.balanceOf(user2) == 0
    assert nft_contract.balanceOf(user3) == 1
