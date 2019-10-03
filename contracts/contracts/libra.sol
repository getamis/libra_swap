pragma solidity >=0.4.22 <0.6.0;

contract Libra {
    bytes32 constant placeholder = "ACCUMULATOR_PLACEHOLDER_HASH\x00\x00\x00\x00";
    bytes4 constant bytes32Length = "\x20\x00\x00\x00";

    bytes constant libraPrefix = "@@$$LIBRA$$@@";
    bytes constant transactionInfoHasher = "TransactionInfo";
    bytes constant transactionAccumulatorHasher = "TransactionAccumulator";

    event ValidationResult(
        bool isValid
    );

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

    function checkMembership(
        bytes memory txInfo,
        bytes32 root,
        bytes32[] memory proof,
        uint256 txVersion,
        uint256 bitmap
    )
        public
    {
        bytes32 txInfoHash = keccak256(abi.encodePacked(
            createHashPrefix(transactionInfoHasher),
            txInfo
        ));
        bool isValid = validateMerkleProof(txInfoHash, txVersion, bitmap, root, proof);

        emit ValidationResult(
            isValid
        );
    }
}
