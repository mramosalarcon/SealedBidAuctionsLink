// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "../node_modules/@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract TimeOracle is Ownable {

    // Pricefeed arrays
    AggregatorV3Interface[] public timeFeed;

    // index of addresses in array mapping
    mapping(address => uint256) public feedToArrayLocation;


    /**
     * @dev Function to add price feed to array.
     * 
     * Requirements:
     *  
     *  -'_newFeed' cannot be in array already.
    */
    function addPriceFeed(address _newFeed) public onlyOwner{
        require(feedToArrayLocation[_newFeed] == 0, 'Pricefeed already in contract');
        AggregatorV3Interface newFeed = AggregatorV3Interface(_newFeed);
        timeFeed.push(newFeed);
        feedToArrayLocation[_newFeed] = timeFeed.length;
    }

    /**
     * @dev Function to delete price feed from array.
     * 
     * Requirements:
     *  
     *  -'_feedToDelete' must be in array already.
    */
    function deletePriceFeed(address _feedToDelete) public onlyOwner{
        require(feedToArrayLocation[_feedToDelete] != 0, 'Pricefeed not in contract');
        uint256 index = feedToArrayLocation[_feedToDelete] - 1;
        feedToArrayLocation[_feedToDelete] = 0;
        timeFeed[index] = timeFeed[timeFeed.length-1];
        timeFeed.pop();
    }

    /**
     * @dev Function retrive the ceiling function of the average time in feeds.
     * 
     * Returns:
     *  
     *  - ceil of average of picefeed times. 
    */
    function getLatestTime() public view returns (uint) {
        uint sumOfTimes;
        uint256 i;
        uint timeStamp;
        for(i = 0; i < timeFeed.length; i++){
            timeStamp = 0;
            ( , , , timeStamp,) = timeFeed[i].latestRoundData();
            sumOfTimes = sumOfTimes + timeStamp;
        }
        return (sumOfTimes + (sumOfTimes % timeFeed.length))/timeFeed.length;
    }

    /**
     * @dev array length getter.
     * 
     * Returns:
     *  
     *  - length of pricefeed array
    */
    function getLength() public view returns (uint){
        return timeFeed.length; 
    }
}