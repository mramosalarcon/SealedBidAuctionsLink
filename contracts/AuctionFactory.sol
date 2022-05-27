// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/KeeperCompatible.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./SealedBidAuction.sol";

contract AuctionFactory is KeeperCompatibleInterface, Ownable, ReentrancyGuard {

    /**
     * @dev Emitted when auction gets moved to state 2.
     */
    event MoveToReveals(uint8 state);

    /**
     * @dev Emitted when auction gets moved to state 3.
     */
    event MoveToWinnerCalculation(uint8 state);

    /**
     * @dev Emitted eth gets to the conact, mostly from comissions.
     */
    event ComissionReceived(uint256 amount);

    /**
     * @dev Emitted when owner retrives eth from comissions.
     */
    event EtherRetrived();

    /**
     * @dev Emitted auction is created.
     */
    event AuctionCreated(address newAuction);

    // Array to store auctions deployed from this factory
    SealedBidAuction[] public sealedBidAuctionArrayContracts;

    // Time offset between time close reveals time and next phase, gives auction owner time to 
    // reveal the minimum price. Set to 5 seconds for testing purposes. 
    uint256 public timeOffset = 5 seconds;

    /**
     * @dev Creates auction and gives ownership of it to creator.
     *
     *
     * Emits a {Transfer} and {AuctionCreated} event.
     */
    function createSealedBidAuctionContract(bytes32 _minimumPriceHash, address _nftContract, uint256 _tokenId, uint _revealTime, uint _winnerTime) public returns (uint256){
        SealedBidAuction auction = new SealedBidAuction(_minimumPriceHash, _nftContract, _tokenId, _revealTime, _winnerTime);
        sealedBidAuctionArrayContracts.push(auction);
        auction.transferOwnership(msg.sender); 
        emit AuctionCreated(address(auction));
    }

    /**
     * @dev Returns last auction address in array
    */
    function getLastAddressInArray() public view returns (address){
        return address(sealedBidAuctionArrayContracts[sealedBidAuctionArrayContracts.length -1]);
    }

    /**
     * @dev Return reveal time for auction `_i` in array
     */
    function getRevealTime(uint256 _i) public view returns (uint256){
        return SealedBidAuction(address(sealedBidAuctionArrayContracts[_i])).revealTime();
    }

    /**
     * @dev Returns close reveals/winner calculation time for auction `_i` in array
    */
    function getWinnerTime(uint256 _i) public view returns (uint256){
        return SealedBidAuction(address(sealedBidAuctionArrayContracts[_i])).winnerTime();
    }

    /**
     * @dev Returns the state of auction `_i` in array
    */
    function getState(uint256 _i) public view returns (SealedBidAuction.AUCTION_STATE){
        return SealedBidAuction(address(sealedBidAuctionArrayContracts[_i])).auction_state();
    }

    /**
     * @dev Changes the state of auction `_i` in array
    */
    function changeState(uint256 _i) internal{
        SealedBidAuction(address(sealedBidAuctionArrayContracts[_i])).nextPhase();
    }

    /**
     * @dev Fallback function
    */
    fallback () payable external {
        emit ComissionReceived(msg.value);
    }

    /**
     * @dev Transfers all funds in factory to address given by owner
     *
     *  Requirements:
     *      Caller is owner,
    */
    function transferFunds(address _address) public nonReentrant onlyOwner{
        payable(_address).transfer(address(this).balance);
    }

    /**
     * @dev Chainlink keepers checkUpkeep function. Checks if an upkeep is needed.
    */
    function checkUpkeep(bytes calldata /* checkData */) external view override returns (bool upkeepNeeded, bytes memory /* performData */) {
        upkeepNeeded = false;
        uint256 i = 0;
        while(i < sealedBidAuctionArrayContracts.length && !upkeepNeeded){
            if(((getWinnerTime(i) + timeOffset < block.timestamp) && (uint8(getState(i)) == 2)) || ((getRevealTime(i) < block.timestamp) && (uint8(getState(i)) == 1))){
                upkeepNeeded = true;
            }
            i++;
        }
    }

    /**
     * @dev Chainlink keepers performUpkeep function, preforms the upkeep.
    */
    function performUpkeep(bytes calldata /* performData */) external override {
        uint256 i;
        for(i = 0; i < sealedBidAuctionArrayContracts.length; i++){
            if((getWinnerTime(i) + timeOffset < block.timestamp) && (uint8(getState(i)) == 2)){
                emit MoveToWinnerCalculation(uint8(getState(i)));
                changeState(i);
            }else if((getRevealTime(i) < block.timestamp) && (uint8(getState(i)) == 1)){
                emit MoveToReveals(uint8(getState(i)));
                changeState(i);
            }
        }
    }

}