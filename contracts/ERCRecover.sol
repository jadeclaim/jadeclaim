// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

contract ErcRecover {
    function extractSignature(bytes memory signature)
        public
        pure
        returns (
            bytes32 r,
            bytes32 s,
            uint8 v
        )
    {
        require(signature.length == 65, "Invalid signature length");

        assembly {
            // Retrieve r by loading the first 32 bytes (offset 0) of the signature
            r := mload(add(signature, 32))

            // Retrieve s by loading the second 32 bytes (offset 32) of the signature
            s := mload(add(signature, 64))

            // Retrieve v by loading the byte (offset 64) following the signature
            v := byte(0, mload(add(signature, 96)))
        }
    }

    function recoverSignerFromSignature(bytes memory signature, bytes32 hash)
        external
        pure
        returns (address)
    {
        (bytes32 r, bytes32 s, uint8 v) = extractSignature(signature);
        address signer = ecrecover(hash, v, r, s);
        return signer;
    }
}
