// SPDX-License-Identifier: MIT
// NFT contract where the tokenURI can be 1 of 3 different dogs
// Randomnly selected
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract CollectibleCreator is ERC721 {
    uint256 public tokenCounter;

    constructor() public ERC721("Non-Fungible Person", "NFP") {
        tokenCounter = 0;
    }

    function createCollectible() public returns (uint256) {
        require(tokenCounter + 1 < 1000);
        uint256 newTokenId = tokenCounter;
        _safeMint(msg.sender, newTokenId);
        //_setTokenURI(newTokenId, tokenURI);
        tokenCounter = tokenCounter + 1;
        return newTokenId;
    }

    function tokenURI(uint256 tokenId)
        public
        view
        virtual
        override
        returns (string memory)
    {
        require(
            _exists(tokenId),
            "ERC721Metadata: URI query for nonexistent token"
        );
        return
            "https://ipfs.io/ipfs/QmWb8W1n3MAbqT1QeSPVraXQ2mJrJDJjggmCjRJtXFBoDQ";
    }
}
