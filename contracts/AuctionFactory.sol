// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./SealedBidAuction.sol";

contract AuctionFactory{

    SealedBidAuction[] public sealedBidAuctionArray;

    function createSealedBidAuctionContract(bytes32 _minimumPriceHash, address _nftContract, uint256 _tokenId, uint _revealTime, uint _winnerTime) public returns (uint256){
        SealedBidAuction auction = new SealedBidAuction(_minimumPriceHash, _nftContract, _tokenId, _revealTime, _winnerTime);
        sealedBidAuctionArray.push(auction);
        auction.transferOwnership(msg.sender); 
    }

    function getLastAddressInArray() public view returns (address){
        return address(sealedBidAuctionArray[sealedBidAuctionArray.length -1]);
    }

}