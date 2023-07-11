// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.7;

import "@openzeppelin/contracts/access/Ownable.sol";

interface IValidSigner {
    function isValidSignature(bytes32 _data, bytes calldata _signature)
        external
        view
        returns (bytes4);
}

interface IGnosis {
    function isValidSignature(bytes calldata _data, bytes calldata _signature)
        external
        view
        returns (bytes4);
}

contract SignatureStorage is Ownable {
    bytes4 public constant ERC1257_MAGICVALUE = 0x1626ba7e;
    bytes4 public constant GNOSIS_MAGICVALUE = 0x20c13b0b;

    bytes32 public HASH;
    mapping(address => bool) public hasSigned;
    string public disclaimer;

    event Signed(address indexed user);

    constructor(bytes32 _hash) {
        HASH = _hash;
    }

    function setHash(bytes32 _hash) external onlyOwner {
        HASH = _hash;
    }

    function canSignFor(address _user) public view returns (bool) {
        if (_user == msg.sender) return true;

        return false;
    }

    function submitSignature(bytes32 hash, bytes memory signature) external returns (bool) {
        require(hash == HASH, "Improper message");
        require(checkSignature(hash, signature, msg.sender), "invalid sig");
        hasSigned[msg.sender] = true;
        emit Signed(msg.sender);
    }

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

    function convertBytes32ToBytes(bytes32 data) public pure returns (bytes memory) {
        bytes memory result = new bytes(32);

        assembly {
            mstore(add(result, 32), data)
        }

        return result;
    }

    function checkForEOA(
        bytes32 hash,
        bytes memory signature,
        address _for
    ) public view returns (bool) {
        (bytes32 r, bytes32 s, uint8 v) = extractSignature(signature);
        address signer = ecrecover(hash, v, r, s);
        return signer == _for;
    }

    function checkGnosis(
        bytes32 hash,
        bytes memory signature,
        address _for
    ) public view returns (bool) {
        bytes memory hashInBytes = convertBytes32ToBytes(hash);
        try IGnosis(_for).isValidSignature(hashInBytes, signature) returns (bytes4 val) {
            return val == GNOSIS_MAGICVALUE;
        } catch {
            return false;
        }
    }

    function checkERC1271(
        bytes32 hash,
        bytes memory signature,
        address _for
    ) public view returns (bool) {
        try IValidSigner(_for).isValidSignature(hash, signature) returns (bytes4 val) {
            return val == ERC1257_MAGICVALUE;
        } catch {
            return false;
        }
    }

    function isContract(address _address) public view returns (bool) {
        uint256 codeSize;
        assembly {
            codeSize := extcodesize(_address)
        }
        return codeSize > 0;
    }

    function checkSignature(
        bytes32 hash,
        bytes memory signature,
        address _for
    ) public view returns (bool) {
        bool isValid;
        if (isContract(_for)) {
            return checkGnosis(hash, signature, _for) || checkERC1271(hash, signature, _for);
        }
        return checkForEOA(hash, signature, _for);
    }

    function setDisclaimer(string calldata _newDisclaimer) external onlyOwner {
        disclaimer = _newDisclaimer;
    }
}
