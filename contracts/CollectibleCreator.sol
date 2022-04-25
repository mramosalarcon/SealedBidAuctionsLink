// SPDX-License-Identifier: MIT
// NFT contract where the tokenURI can be 1 of 3 different dogs
// Randomnly selected
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract CollectibleCreator is ERC721URIStorage{

    uint256 public tokenCounter;

    constructor () public ERC721 ("TestingToken", "TT"){
        tokenCounter = 0;
    }

    function createCollectible(string memory tokenURI) public returns (uint256){
        uint256 newTokenId = tokenCounter;
        _safeMint(msg.sender, newTokenId);
        _setTokenURI(newTokenId, tokenURI);
        tokenCounter = tokenCounter + 1;
        return newTokenId;
    }


}
