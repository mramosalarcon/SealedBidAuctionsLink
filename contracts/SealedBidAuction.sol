// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * Sealed Bid auction protocol. 
*/

contract SealedBidAuction is Ownable, ReentrancyGuard {

    // Participant wallets array.
    address[] public players;

    // Wallet to amount transfered mapping.
    mapping(address => uint256) public accountToAmount;

    // Wallet to hash of offer + secret mapping.
    mapping(address => bytes32) public accountToHash;

    // Wallet to offer mapping
    mapping(address => uint256) public accountToOffer;

    // Auction winner
    address public winner;

    // Auction sale price.
    uint256 public amount;

    // Hash of minPrice + secret
    bytes32 public minimumPriceHash;

    // minimum price of token
    uint256 public minimumPrice;

    // NFT 
    IERC721 public parentNFT;

    // NFT ID
    uint256 public tokenId;


    // Time when acution changes to reveals == Time when offers close
    uint public revealTime;

    // Time when winner is calculated == Time when reveals close
    uint public winnerTime;

    // Time offset to let owner reveal price
    uint public timeOffset = 5 seconds;

    // States of the auction
    enum AUCTION_STATE{
        CONTRACT_CREATION,
        RECIVEING_OFFERS,
        OFFER_REVEAL,
        CALCULATING_WINNER,
        AUCTION_ENDED
    }

    /**
     * @dev Emitted when contract receives token.
     */
    event ERC721Transfer();

    /**
     * @dev Emitted when `account` makes a secret offer of `hashString`.
     */
    event OfferMade(address account, bytes32 hashString);

    /**
     * @dev Emitted when auction states moves to RECEIVEINF_OFFERS.
     */
    event OffersClosed();

    /**
     * @dev Emitted when `accounts` reveals offer of `price` and `secret`
     */
    event OfferRevealed(address account, string secret, uint256 amount);

    /**
     * @dev Emitted when owner reveals minimum price `amaount`.
     */
    event MinimumPriceRevealed(uint256 amount);

    /**
     * @dev Emitted when `account` wins the auction for an offered `amount`
     */
    event WinnerChosen(address account, uint256 amount);

    /**
     * @dev Emitted when owner get payed `amount`
     */
    event OwnerPayed(uint256 amount);

    /**
     * @dev Emitted when `account` is reinbursed `amount`
     */
    event ParticipantReimbursed(address account, uint256 amount);

    /**
     * @dev Emitted when `account` retrives ERC721.
     */
    event TokenWithdrawal(address account);


    // Stores the auction of the state
    AUCTION_STATE public auction_state;

    /**
     * @dev Auction constructor 
     * Constructs the auction contract.
     * Requirements:
     *  
     *  -'_nftContract' cannot be zero address
    */

    constructor(bytes32 _minimumPriceHash, address _nftContract, uint256 _tokenId, uint _revealTime, uint _winnerTime) {
        require(_nftContract != address(0), "Not a valid ERC721 address");
        auction_state = AUCTION_STATE.CONTRACT_CREATION;
        minimumPriceHash = _minimumPriceHash;
        parentNFT = IERC721(_nftContract);
        tokenId = _tokenId;
        revealTime = _revealTime;
        winnerTime = _winnerTime;
    }

    /**
     * @dev Transfers ERC721 to contract
     * 
     * Requirements:
     *  -Auction state must be CONTRACT_CREATION
     *
     * Emits a {ERC721Transfer} event. 
    */


    function transferAssetToContract() public onlyOwner{
        require(auction_state == AUCTION_STATE.CONTRACT_CREATION);
        parentNFT.transferFrom(_msgSender(), address(this), tokenId);
        auction_state = AUCTION_STATE.RECIVEING_OFFERS;
        emit ERC721Transfer();
    }

    /**
     * @dev Lets a participant make an offer
     * 
     * Requirements:
     *  -Auction state must be RECIVEING_OFFERS
     *  -Contract owner cant make an offer
     *  -Must transfer a non zero amount of eth
     *
     * Emits a {OfferMade} event. 
    */

    
    function makeOffer(bytes32 _hash) public virtual payable{
        require(auction_state == AUCTION_STATE.RECIVEING_OFFERS, 'Wrong auction state');
        require(_msgSender() != owner(), "Owner cant bid");
        require(msg.value > 0, "Need some ETH");
        require(accountToAmount[_msgSender()] == 0, "Cant bid twice"); 
        players.push(payable(_msgSender()));
        accountToAmount[_msgSender()] = msg.value;
        accountToHash[_msgSender()] = _hash;
        emit OfferMade( _msgSender(), _hash);
    }

    /**
     * @dev Changes state of auction to offer reveals
     * 
     * Requirements:
     *  -Time origin must be larger than contract set time
     *  -Auction state must be in RECIVEING_OFFERS
     *  -Must transfer a non zero amount of eth
     *
     * Emits a {OffersClosed} event. 
    */
    function closeOffers() public{
        require(block.timestamp >= revealTime, 'Wait until set time');
        require(auction_state == AUCTION_STATE.RECIVEING_OFFERS, 'Wrong auction state');
        auction_state = AUCTION_STATE.OFFER_REVEAL;
        emit OffersClosed();
    }

    /**
     * @dev Reveals offer of participants
     * 
     * Requirements:
     *  -   accountToAmount[_msgSender()] must not be zero
     *  -   accountToOffer[_msgSender()] must be zero. Prevents double reveals
     *  -   Auction state must be in OFFER_REVEAL
     *  -   Must transfer a non zero amount of eth
     *  -   _amount must be equal or smaller to accountToAmount[_msgSender()]
     *  -   _secret and _amount hash must match stored hash
     *
     *
     * Emits a {OfferRevealed} event. 
    */

    function revealOffer(string memory _secret, uint256 _amount) public virtual{
    require(auction_state == AUCTION_STATE.OFFER_REVEAL, "Not right time");
    require(accountToAmount[_msgSender()] != 0, "You are not a participant"); 
    require(accountToOffer[_msgSender()] == 0, "Can only reveal once"); 
    require(_amount <= accountToAmount[_msgSender()], "Offer invalidated"); 
    require(
        accountToHash[_msgSender()] == keccak256(
            abi.encodePacked(
                _secret,
                _amount
            )
        ), "Hashes do not match"
    );
        accountToOffer[_msgSender()] = _amount;
        emit OfferRevealed(_msgSender(), _secret, _amount);
    }

    /**
     * @dev Changes auction state to CALCULATING_WINNER
     * 
     * Requirements:
     *  -   caller must not be owner
     *  -   time origin must be larger than preset closeReveals time
     *  -   Auction state must be in OFFER_REVEAL
     *
     *
     * Calls _closeReveals() Internal funciton. 
    */

    function closeReveals() public{
        require(block.timestamp >= winnerTime + timeOffset, 'Wait until set time + offset'); //5s despues que vence tiempo de owner
        require(_msgSender() != owner(), "Owner must use winnerCalculation()");
        require(auction_state == AUCTION_STATE.OFFER_REVEAL, 'wrong auction state');
        auction_state = AUCTION_STATE.CALCULATING_WINNER;
        _closeReveals();
    }

    /**
     * @dev Owner reveals minimum price and calculates winner
     * 
     * Requirements:
     *  -   caller must be owner
     *  -   Auction state must be in OFFER_REVEAL
     *  -   time origin must be larger than preset closeReveals time
     *  -   _secret and _amount hash must match stored hash
     *
     *
     * Emits a {MinimumPriceRevealed} event. 
    */

    // TODO un cambio de nombre no vendria mal, creo. Poco intuitivo.?
    function winnerCalculation(string memory _secret, uint256 _amount) public onlyOwner {
        require(auction_state == AUCTION_STATE.OFFER_REVEAL, 'Wrong auction state');
        require(block.timestamp >= winnerTime, 'Wait until set time');
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
        emit MinimumPriceRevealed(_amount);
        _closeReveals();
    }

    /**
     * @dev Closes reveal period and calculates winner, intenal
     * 
     *
     * Emits a {WinnerChosen} event. 
    */

    function _closeReveals() internal{
        uint256 indexOfWinner;
        uint256 loopAmount;
        uint256 i;
        if(players.length > 0){
            for(i = 0; i < players.length; i++){
                if(accountToOffer[players[i]] > loopAmount){
                    indexOfWinner = i;
                    loopAmount = accountToOffer[players[i]];
                }
            }
            if(loopAmount >= minimumPrice){
                winner = players[indexOfWinner];
                amount = accountToOffer[winner];
                accountToAmount[winner] = accountToAmount[winner] - accountToOffer[winner];
            } 
        }
        auction_state = AUCTION_STATE.AUCTION_ENDED;
        emit WinnerChosen(winner, amount);
    }

    /**
     * @dev Auction owner retrives sale price or nft if it did not sell
     * 
     * Requirements:
     *  -   caller must be owner
     *  -   Auction state must be in AUCTION_ENDED
     *
     *
     * Emits a {OwnerPayed} xor {TokenWithdrawal} event. 
    */

    function ownerGetsPayed() public onlyOwner nonReentrant{
        require(auction_state == AUCTION_STATE.AUCTION_ENDED);
        if(amount > 0){
            uint256 toPay = amount;
            amount = 0;
            payable(owner()).transfer(toPay);
            emit OwnerPayed(toPay);
        }else{
            parentNFT.safeTransferFrom(address(this), _msgSender(), tokenId);
            emit TokenWithdrawal(owner());
        }
    }

    /**
     * @dev Reinburses deposited amount left to participants after auction ends
     * 
     * Requirements:
     *  -   Auction state must be in AUCTION_ENDED
     *  -   accountToAmount[_msgSender()] must be larger than 0
     *
     *
     * Emits a {ParticipantReimbursed} event. 
    */

    function reimburseParticipant() nonReentrant public{
        require(auction_state == AUCTION_STATE.AUCTION_ENDED);
        uint256 reimbursement = accountToAmount[_msgSender()];
        require(reimbursement > 0);
        accountToAmount[_msgSender()] = 0;
        payable(_msgSender()).transfer(reimbursement);
        emit ParticipantReimbursed(_msgSender(), reimbursement);
    }

    /**
     * @dev Auction winner retrives ERC721 token.
     * 
     * Requirements:
     *  -   Auction state must be in AUCTION_ENDED
     *  -   caller must be auction winner
     *
     *
     * Emits a {TokenWithdrawal} event. 
    */

    function winnerRetrivesToken() nonReentrant public{
        require(auction_state == AUCTION_STATE.AUCTION_ENDED);
        require(_msgSender() == winner);
        parentNFT.safeTransferFrom(address(this), _msgSender(), tokenId);
        emit TokenWithdrawal(_msgSender());
    }
}