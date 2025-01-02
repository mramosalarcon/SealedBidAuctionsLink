// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract SimpleNFT is ERC721, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    constructor() ERC721("SimpleNFT", "SNFT") {}

    // Mint new NFT
    function mintNFT(address recipient) public onlyOwner returns (uint256) {
        _tokenIds.increment();
        uint256 newTokenId = _tokenIds.current();
        
        _safeMint(recipient, newTokenId);
        return newTokenId;
    }

    // Transfer NFT
    function transferNFT(address from, address to, uint256 tokenId) public {
        require(_isApprovedOrOwner(_msgSender(), tokenId), "Transfer caller is not owner nor approved");
        safeTransferFrom(from, to, tokenId);
    }
}
