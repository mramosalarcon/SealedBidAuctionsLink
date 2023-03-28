# [LIVE ON ARBITRUM](https://auctionator.xyz/)

# Auctionator (Sealed Bid Auctions for ERC-721 Tokens)

CompEng Thesis Project. Here you will find the implementation of a sealed bid auction protocol for ERC-721 tokens that uses chainlink keepers to automate auction execution.

# Introduction

## Inspiration

NFT market movement is and has been a hot topic. In many NFT projects we've seen floor prices go through the roof just to hit rock bottom a few days or months later. This floor price flutuations can be due a lot of things: FUD, project anouncements, external factors and market manipulation. The problem we found was that, in many projects, the most popular way of estimaing the value of a token or a collection is with the price of the last sale made and the floor price on secondary markets, which is not the best. Imagine the following scenarios:

1. An artist is selling an NFT and 100 people interested. Lets say that 99 would pay 1 eth for the token and one single buyer offers 100 eth. So, would it be right to think the NFT is ACTUALLY worth 100 eth when 99% of interested buyers were not willing to pay more than 1?

2. A new NFT collection of 100 tokens is soldout. In secondary markets the floor price is at 1 eth and there are 99 tokens listed at that price. Someone also listed a token for 100eth. Imagine all tokens bought and not relisted so the only one for sale is at 100 eth. Does that mean that all other tokens are worth that and that the collection "marketcap" is 10,000 eth?

The answer to those questions is rather hard, this project is about paving the way of a better NFT market valuation method. Most NFT markets are relativly small, have a very limited supply and are not very liquid. We could compre some NFT markets to the radiofrequency markets, only a handfull of operators exists and are interested in buying/renting part of the spectrum, for them certain bands are worth billions but for almost anyone else, why would you want a band? The way they buy/rent this pices of the spectrum is via auctions, because it is a relativly small market, have a very limited supply and are not very liquid, same as an NFT market.

## What it does

This project is a Sealed Bid or Closed Auction protocol for ERC-721 tokens.

### Sealed Bid Auction:

A type of Auction where interested parties write down a secret offer and seal it. all sealed offers are latter opened together and whoever offered the most wins the auction. There are 2 formats, one where the winner pays what he offered and a second one where the winner pays what the second place offered + 1 unit (vickrey format). We will use the first approach.

### How does this type auction help valuate a token better?

Lets go back to the first scenario. If 100 people made an offer, 99 where for 1 eth and 1 was for 100 eth we would know that 99% of the market values the token at 1 eth but that it was sold to some crazy participant for 100. This does not happen in todays NFT markets, we think a token is woth x just because that was the last price, we have no way of "asking" all the interested people what the token is worth. Selling a token in this type of auction will tell us what most people are willing to pay rather than what 1 crazy wallet payed.

## How we built it

The auction itself is a Soidity contract. In the auction there are 5 stages: initialization, receiving offers, offer reveal, winner calculation and auction ended. Moving from the second to the third stage and from the third to the fourth stage is done with chainlink keepers.

We also made an auction factory contract that deploys auctions and is the contract that implements the keepers interface so all deployed auctions can be mantained. The keepers fees will be payed by the revenue generated from running auctions, we hardcoded a 2% comission on each NFT sale that will be transfered back to the factory once ended auction has ended.

![img](<./img/flujo-subasta-2(3).png>)

We used the brownie library for developing and testing our contract. Tests where run in ganache and rinkeby. React, useDapp, ethersjs and the AlchemyNFT API for the frontend. And finally Netlify for frontend deployment. The frontend is connected to an auction factory running in Rinkeby.

## Challenges we ran into

The whole projct was a challenge, from finding a possible way to make better market valuations (closed auctions), testing the contracts, imagining possible auction scenarios. Also, the frontend was a very challenging part, it works but there is A LOT that could be better. But the important part is that it's functional.

## Accomplishments that we're proud of

We are proud of the protocol and the contract, the code runs perfectly. It still probably has bugs but none that we could find with the tests we wrote. I really enjoyed this experience.

## What we learned

The biggest lesson we (I) learned was that the best thing to do when writing a smart contract is to have a well thought plan. Programming smart contracts is not the same as other types of programming, you can't just "Ape in" and see what happens. A well structured plan pays off timeways in the end. I also fell in love with smart contract development, finding bugs is actually entretaining. We learned that chainlink keepers are very easy to use, but we would recommend a feature: Be able to create an upkeep with a range of values in `checkData` instead of having to create an upkeep for each value. It would be nice but not really necesary.

## What's next for NFT-SealedBidAuction

Now that we have a decent contract the plan is the next:

1. Test the contract even more, decent does not mean good.
2. Extend soupport for ERC1155 NFTs.
3. Let the auctioneer set a timeOffset from the times reveals close and the time the auctioneer has to reveal his minimum price.
4. Make a better frontend, display more data there
5. Develop auction reading tools so we can graph the distribution of offers

If we were to one day lauch the project:

1. Get an auditor.
2. First, test a final version on a L2, see ehat people do with it.
3. Create an auction factory factory contract, limit the amounts of acutions in a factory
4. Evaluate how many auctions per factory is a good number, thisdepends of keeper costs and mean revenue per auction hosted.

# Testing instructions

For thesting the contract you must have brownie installed and a few other dependencies. Once you have them do `$ brownie test` and tests will run.

The frotend is available on the following [link](https://auctionator.xyz/). You need Rinkeby eth to run and participate in auctions.

# Frontend FAQs

### Create Auction

#### How do I create an auction?

- Just click the token you want to auction and the create auction screen will open.

#### Fields you need to fill out:

1. Minimum price: The minimum price you are willing to receive for your NFT
2. Secret: A secret word, this, along with the price will be encripted, latter you mus reveal them
3. Close offers date: When offers close
4. close reveals date: When reveals close

#### Approve and deposit tokens:

- For the auction to be created the contract must hold the token you want to auciton.

### Live Auctions

Here you will see what auctions have been created from the set auction factory and what stage they are in. If there is no image it is because the NFT left the contract! (It was claimed by the auction winner).

#### How can I make an offer?

- Just click an auction that is in the Offers period and a form will appear. You must fill out a few things:
  1. Price: what you are willing to pay
  2. Secret: The secret word that will be used to encrypt your offer
  3. Amount to send: The protocol needs to recive at least your offer (only you know what your offer is) fir the reveal and offer to be valid. Lets say you offer 0.1 eth and send 20 eth. Only you know what you offered but can deceive people! Dont worry, you will get all your eth back once the acution has ended. Be sure to send more than what you are offering. We do this to make sure all offers can be payed for.
- Remember to come back to reveal your offer! The time for that shows on your screen.

#### How do I reveal?

- You go into the auction during the reveals phase and enter your secret and offer. If you forgot them you wont be able to reveal them but you will still get your eth back once the auction ends.

#### When do reveals end?

- Reveals end at the set time + 60 minutes. This 60 minutes let the auctioneer reveal his minimum price. But do not worry, if he does not reveal the price then it will be set to 0 and the auction will continue.

#### How do I know if I won?

- Once reveals are over the winner is calculated and publish in the auction page, enter the auction to check if you won! If you did you will be able to claim the token + the extra eth you sent. So if you sent 1 eth, offered 0.1 eth and won the you can get the token and 0.9 eth.

#### What if I did not win?

- You can claim back your eth, just visit the page and you will see how.

#### As the auctioneer, how do I reveal the minimum price?

- When reveal time ends you will have 2 minutes to reveal your minimum price, if not it will be set to 0 but tont worrk you sill still get payed, just maybe not above what you where asking for.

#### I auctioned the NFT, what if there are no offers that match my minimum price?

- You will get your NFT back.

### Free Mint

- Just a free NFT mint you you can test the protocol.
