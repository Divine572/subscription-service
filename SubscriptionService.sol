// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SubscriptionService {
    address public owner;
    uint256 public subscriptionPrice;

    struct Subscriber {
        bool isActive;
        uint256 expirationTime;
    }

    mapping(address => Subscriber) public subscribers;

    event Subscribed(address indexed subscriber, uint256 expirationTime);

    constructor(uint256 _subscriptionPrice) {
        owner = msg.sender;
        subscriptionPrice = _subscriptionPrice;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "You are not the owner");
        _;
    }

    modifier onlyActiveSubscribers() {
        require(
            subscribers[msg.sender].isActive &&
                subscribers[msg.sender].expirationTime > block.timestamp,
            "You must be an active subscriber"
        );
        _;
    }

    function subscribe() external payable {
        require(
            msg.value == subscriptionPrice,
            "Must send exact subscription price"
        );

        subscribers[msg.sender].isActive = true;
        subscribers[msg.sender].expirationTime = block.timestamp + 30 days;

        emit Subscribed(msg.sender, subscribers[msg.sender].expirationTime);
    }

    function withdrawFunds(uint256 _amount) external onlyOwner {
        payable(owner).transfer(_amount);
    }
}
