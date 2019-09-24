pragma solidity >=0.4.22 <0.6.0;

contract AtomicSwap {
    uint32 constant refundLength = 10 minutes;

    struct Swap {
        address initiator;
        address receiver;
        uint amount;
        uint startTime;
        uint refundTime;
        bool isFinished;
    }

    mapping(bytes32 => Swap) public swaps;

    // events
    event Initiated(
        address initiator,
        address receiver,
        uint amount,
        uint startTime,
        uint refundTime,
        bytes32 hashedSecret
    );
    event Redeemed(uint redeemTime);
    event Refunded(uint refundTime);

    // initiate
    function initiate(address receiver, bytes32 hashedSecret)
        external payable
    {
        // conditional check
        require(!swaps[hashedSecret].isFinished);
        require(msg.value > 0);

        // swap data
        Swap memory swap;

        swap.initiator = msg.sender;
        swap.receiver = receiver;
        swap.amount = msg.value;
        swap.startTime = now;
        swap.refundTime = now + refundLength;
        swap.isFinished = false;
        swaps[hashedSecret] = swap;

        // event
        emit Initiated(
            swap.initiator,
            swap.receiver,
            swap.amount,
            swap.startTime,
            swap.refundTime,
            hashedSecret
        );
    }

    // redeem
    function redeem(bytes memory secret) public {
        bytes32 _hashedSecret = keccak256(secret);

        Swap memory swap = swaps[_hashedSecret];

        // conditional check
        require(!swap.isFinished);
        require(now < swap.refundTime);
        require(swap.receiver == msg.sender);

        // transfer
        swap.isFinished = true;
        msg.sender.transfer(swap.amount);

        // event
        emit Redeemed(now);
    }

    // refund
    function refund(bytes32 hashedSecret) external {
        Swap memory swap = swaps[hashedSecret];

        // conditional check
        require(!swap.isFinished);
        require(now > swap.refundTime);
        require(swap.initiator == msg.sender);

        // transfer
        swap.isFinished = true;
        msg.sender.transfer(swap.amount);

        // event
        emit Refunded(now);
    }
}