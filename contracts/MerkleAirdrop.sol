//SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import "../interfaces/ISignatureStorage.sol";

contract MerkleAirdrop is Ownable {
    using SafeERC20 for IERC20;
    // This is a packed array of booleans.
    bytes32 public root;

    uint256 public totalClaimed;
    // This event is triggered whenever a call to #claim succeeds.
    mapping(address => bool) public claimedAddresses;

    IERC20 public token;

    ISignatureStorage public signatureStorage;

    event Claimed(address account, uint256 amount);

    constructor(IERC20 _token, ISignatureStorage _signatureStorage) {
        token = _token;
        signatureStorage = _signatureStorage;
    }

    function testProof(
        address account,
        uint256 amount,
        bytes32[] calldata merkleProof
    ) public view returns (bool) {
        bytes memory k = abi.encode(account, amount);
        bytes32 node = keccak256(bytes.concat(keccak256(k)));
        return MerkleProof.verify(merkleProof, root, node);
    }

    function claim(
        address account,
        uint256 amount,
        bytes32[] calldata merkleProof
    ) external {
        // Verify the merkle proof.
        require(signatureStorage.hasSigned(account), "user has not signed");
        bytes32 node = keccak256(bytes.concat(keccak256(abi.encode(account, amount))));
        require(!claimedAddresses[account], "Drop already claimed.");
        require(MerkleProof.verify(merkleProof, root, node), "Invalid proof.");

        // Mark it claimed and send the token.
        claimedAddresses[account] = true;
        token.safeTransfer(account, amount);
        totalClaimed += amount;

        emit Claimed(account, amount);
    }

    function setRoot(bytes32 _root) external onlyOwner {
        root = _root;
    }

    function scoopTokens(IERC20 _token) external onlyOwner {
        _token.safeTransfer(owner(), _token.balanceOf(address(this)));
    }
}
