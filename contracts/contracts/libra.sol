pragma solidity >=0.4.22 <0.6.0;

contract Libra {
    bytes32 constant placeholder = "ACCUMULATOR_PLACEHOLDER_HASH\x00\x00\x00\x00";
    bytes constant libraPrefix = "@@$$LIBRA$$@@";
    bytes constant transactionInfoHasher = "TransactionInfo";
    bytes constant transactionAccumulatorHasher = "TransactionAccumulator";
    uint32 constant refundLength = 1 hours;

    /*
     * Storage
     */
    struct Deposit {
        address depositor;
        address beneficiary;
        uint amount;
        uint startTime;
        uint refundTime;
    }

    uint256 public counter;
    mapping(uint256 => Deposit) public deposits;

    /*
     * Events
     */
    event DepositEvent(
        uint256 depositID,
        address depositor,
        address beneficiary,
        uint amount,
        uint startTime,
        uint refundTime
    );

    event TransferEvent(
        uint transferTime
    );

    event ChallengeEvent(
        bool isValid,
        uint challengeTime
    );

    event RefundEvent(
        uint refundTime
    );

    /*
     * Public functions
     */
    function deposit(address beneficiary) public payable {
        // conditional check
        require(msg.value > 0, "deposit should not be zero");

        Deposit memory d;

        d.depositor = msg.sender;
        d.beneficiary = beneficiary;
        d.amount = msg.value;
        d.startTime = now;
        d.refundTime = now + refundLength;
        deposits[counter] = d;

        // event
        emit DepositEvent(
            counter,
            d.depositor,
            d.beneficiary,
            d.amount,
            d.startTime,
            d.refundTime
        );

        // increment the counter
        counter++;
    }

    function transfer(uint256 depositID, uint amount) public {
        Deposit memory d = deposits[depositID];

        // conditional check
        require(now < d.refundTime, "deposit should not be expired");
        require(d.depositor == msg.sender, "sender should be depositor");
        require(d.amount > amount, "transfer amount should be less than deposit");

        address(uint160(d.beneficiary)).transfer(amount); // send ether to beneficiary
        msg.sender.transfer(d.amount - amount); // send remaining ether back to depositor
        delete deposits[depositID]; // case closed

        emit TransferEvent(now);
    }

    function challenge(
        uint256 depositID,
        bytes memory txInfo,
        bytes32 root,
        bytes32[] memory proof,
        uint256 txVersion,
        uint256 bitmap
    )
        public
    {
        Deposit memory d = deposits[depositID];

        // conditional check
        require(now < d.refundTime, "deposit should not be expired");
        require(d.beneficiary == msg.sender, "sender should be beneficiary");

        // generate the hash of transaction info
        bytes32 txInfoHash = keccak256(abi.encodePacked(
            createHashPrefix(transactionInfoHasher),
            txInfo
        ));

        // TODO: Here, we only validate the merkle proof of a Libra transaction. However, there is some room for improvement.
        // 1. Merkle root should be updated by a trusted source periodically, not provided by the challenger.
        // 2. We should also check the information in this transaction like sender, receiver, timestamp to prevent fraud.
        bool isValid = validateMerkleProof(txInfoHash, txVersion, bitmap, root, proof);

        if (isValid) {
            // punish depositor by sending deposit to beneficiary
            address(uint160(d.beneficiary)).transfer(d.amount);
            delete deposits[depositID];
        }

        emit ChallengeEvent(isValid, now);
    }

    function refund(uint256 depositID) public {
        Deposit memory d = deposits[depositID];

        // conditional check
        require(now > d.refundTime, "deposit should be expired");
        require(d.depositor == msg.sender, "sender should be depositor");

        // transfer
        msg.sender.transfer(d.amount);
        delete deposits[depositID];

        // event
        emit RefundEvent(now);
    }

    /*
     * Internal functions
     */
    function createHashPrefix(bytes memory salt)
        internal
        pure
        returns (bytes32)
    {
        // TODO: change hash function
        return keccak256(abi.encodePacked(salt, libraPrefix));
    }

    function validateMerkleProof(
        bytes32 leaf,
        uint256 txVersion,
        uint256 bitmap,
        bytes32 rootHash,
        bytes32[] memory proof
    )
        internal
        pure
        returns (bool)
    {
        bytes32 computedHash = leaf;
        uint256 index = proof.length - 1;
        while (bitmap > 0) {
            bytes32 sibling;
            if (bitmap % 2 == 0) {
                sibling = placeholder;
            } else {
                assert(index >= 0);
                sibling = proof[index];
                index = index - 1;
            }

            // TODO: change hash function
            if (txVersion % 2 == 0) {
                computedHash = keccak256(abi.encodePacked(createHashPrefix(transactionAccumulatorHasher), computedHash, sibling));
            } else {
                computedHash = keccak256(abi.encodePacked(createHashPrefix(transactionAccumulatorHasher), sibling, computedHash));
            }
            bitmap = bitmap / 2;
            txVersion = txVersion / 2;
        }

        return computedHash == rootHash;
    }
}
