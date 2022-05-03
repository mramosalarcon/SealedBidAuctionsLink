// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";

contract SealedBidAuction is Ownable, IERC721Receiver {


    address[] public players; // Para poder regresar x a los que no ganan

    mapping(address => uint256) public accountToAmount;
    mapping(address => bytes32) public accountToHash;
    mapping(address => uint256) public accountToOffer;

    address public winner;
    uint256 public amount;
    bytes32 public minimumPriceHash;
    uint256 public minimumPrice;

    IERC721 public parentNFT;
    uint256 public tokenId;

    enum AUCTION_STATE{
        CONTRACT_CREATION,
        RECIVEING_OFFERS,
        OFFER_REVEAL,
        CALCULATING_WINNER,
        AUCTION_ENDED
    }

    AUCTION_STATE public auction_state;

    constructor(bytes32 _minimumPriceHash, address _nftContract, uint256 _tokenId) {
        auction_state = AUCTION_STATE.CONTRACT_CREATION;
        minimumPriceHash = _minimumPriceHash;
        parentNFT = IERC721(_nftContract);
        tokenId = _tokenId;
    }

    function transferAssetToContract() public onlyOwner{
        parentNFT.safeTransferFrom(_msgSender(), address(this), tokenId);
        auction_state = AUCTION_STATE.RECIVEING_OFFERS;
    }

    
    function makeOffer(bytes32 _hash) public virtual payable{
        require(auction_state == AUCTION_STATE.RECIVEING_OFFERS);
        require(_msgSender() != owner(), "Owner cant bid");
        require(msg.value > 0, "Need some ETH");
        require(accountToAmount[_msgSender()] == 0, "Cant bid twice"); // New participant.
        //event
        players.push(payable(_msgSender()));
        //event
        accountToAmount[_msgSender()] = msg.value;
        //event
        accountToHash[_msgSender()] = _hash;
    }

    function closeOffers() public onlyOwner {
        require(auction_state == AUCTION_STATE.RECIVEING_OFFERS);
        auction_state = AUCTION_STATE.OFFER_REVEAL;
    }

    // Cambiale el nombre y pega el close reveals a final del metodo. Te mamas 
    function winnerCalculation(string memory _secret, uint256 _amount) public onlyOwner {
        require(auction_state == AUCTION_STATE.OFFER_REVEAL);
        require(
            minimumPriceHash == keccak256(
                abi.encodePacked(
                    _secret,
                    _amount
                )
            ), "Hashes do not match"
        );
        minimumPrice = _amount;
        auction_state = AUCTION_STATE.CALCULATING_WINNER;
        _closeReveals();
    }

    function revealOffer(string memory _secret, uint256 _amount) public virtual{
        require(auction_state == AUCTION_STATE.OFFER_REVEAL, "Not right time");
        require(accountToAmount[_msgSender()] != 0, "You are not a participant"); // Participant
        require(accountToOffer[_msgSender()] == 0, "Can only reveal once"); // No retrys
        require(_amount <= accountToAmount[_msgSender()], "Offer invalidated"); 
        require(
            accountToHash[_msgSender()] == keccak256(
                abi.encodePacked(
                    _secret,
                    _amount
                )
            ), "Hashes do not match"
        ); // Hash match
        //event
        accountToOffer[_msgSender()] = _amount;
    }
    //Funcion para recibir el precio minimo

    function _closeReveals() internal onlyOwner { //internal
        // Verifia que el precio minimo este puesto. 
        require(auction_state == AUCTION_STATE.CALCULATING_WINNER);
        uint256 indexOfWinner;
        uint256 loopAmount;
        uint256 i;
        for(i = 0; i < players.length; i++){
            if(accountToOffer[players[i]] > loopAmount){
                indexOfWinner = i;
                loopAmount = accountToOffer[players[i]];
            }
    
        }
        if(loopAmount >= minimumPrice){
            winner = players[indexOfWinner];
            amount = accountToOffer[winner];
            // Quito lo ofrecido al que gana
            accountToAmount[winner] = accountToAmount[winner] - accountToOffer[winner];
        }
        auction_state = AUCTION_STATE.AUCTION_ENDED;
    }

    function ownerGetsPayed() public onlyOwner{
        require(auction_state == AUCTION_STATE.AUCTION_ENDED);
        if(amount > 0){
            uint256 toPay = amount;
            amount = 0; //No reentrancy
            payable(owner()).transfer(toPay);
        }else{
            // Nadie gana entonces regresa NFT al que crea subasta.
            parentNFT.safeTransferFrom(address(this), _msgSender(), tokenId);
        }
    }

    function reimburseParticipant() public{
        // Tenga saldo positivo
        require(auction_state == AUCTION_STATE.AUCTION_ENDED);
        uint256 reimbursement = accountToAmount[_msgSender()];
        require(reimbursement > 0);
        accountToAmount[_msgSender()] = 0; // no reent
        payable(_msgSender()).transfer(reimbursement);
    }

    function winnerRetrivesToken() public{
        require(auction_state == AUCTION_STATE.AUCTION_ENDED);
        require(_msgSender() == winner);
        parentNFT.safeTransferFrom(address(this), _msgSender(), tokenId);
    }

    function onERC721Received(
        address operator,
        address from,
        uint256 tokenId,
        bytes calldata data
    ) public virtual override returns (bytes4){
         return this.onERC721Received.selector;
    }
}