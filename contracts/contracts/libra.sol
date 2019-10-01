pragma solidity >=0.4.22 <0.6.0;

contract Libra {
    bytes32 constant placeholder = "ACCUMULATOR_PLACEHOLDER_HASH\x00\x00\x00\x00";
    bytes4 constant bytes32Length = "\x20\x00\x00\x00";

    bytes constant libraPrefix = "@@$$LIBRA$$@@";
    bytes constant transactionInfoHasher = "TransactionInfo";
    bytes constant transactionAccumulatorHasher = "TransactionAccumulator";

    function createHashPrefix(bytes memory salt)
        internal
        pure
        returns (bytes32)
    {
        // TODO: change hash function
        return keccak256(abi.encodePacked(salt, libraPrefix));
    }

    function checkMembership(
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

    function doesTxExist(
        bytes32 signedTx,
        bytes32 stateRoot,
        bytes32 eventRoot,
        uint64 gasUsed,
        uint64 majorStatus,
        bytes32 root,
        bytes32[] memory proof,
        uint256 txVersion,
        uint256 bitmap
    )
        public
        pure
        returns (bool)
    {
        bytes32 txInfo = keccak256(abi.encodePacked(
            createHashPrefix(transactionInfoHasher),
            bytes32Length,
            signedTx,
            bytes32Length,
            stateRoot,
            bytes32Length,
            eventRoot,
            gasUsed,
            majorStatus));
        return checkMembership(txInfo, txVersion, bitmap, root, proof);
    }
}
