// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/introspection/IERC165.sol";

/**
 * Sealed Bid auction protocol. 
*/

interface SealedBidAuction is IERC165{


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

    /**
     * @dev Transfers ERC721 to contract
     * 
     * Requirements:
     *  -Auction state must be CONTRACT_CREATION
     *
     * Emits a {ERC721Transfer} event. 
    */


    function transferAssetToContract() external ;

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

    
    function makeOffer(bytes32 _hash) external virtual payable;

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
    function closeOffers() external;

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

    function revealOffer(string memory _secret, uint256 _amount) external virtual;

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

    function closeReveals() public;

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
    function winnerCalculation(string memory _secret, uint256 _amount) external;


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

    function ownerGetsPayed() external;

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

    function reimburseParticipant() external;

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

    function winnerRetrivesToken() external;
}