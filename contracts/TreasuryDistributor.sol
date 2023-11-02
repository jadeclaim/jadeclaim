// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Pausable} from "@openzeppelin/contracts/utils/Pausable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {MerkleProof} from "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import {IERC20, SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import {ISignatureStorage} from "./interfaces/ISignatureStorage.sol";

contract TreasuryDistributor is Pausable, ReentrancyGuard, Ownable {
	using SafeERC20 for IERC20;

	IERC20 public immutable usdc;
	uint256 public immutable MAXIMUM_AMOUNT_TO_CLAIM;

	bool public isMerkleRootSet;
	bytes32 public merkleRoot;
	uint256 public endTimestamp;
	ISignatureStorage public signatureStorage;

	mapping(address => bool) public hasClaimed;

	event Claimed(address indexed user, uint256 amount);
	event MerkleRootSet(bytes32 merkleRoot);
	event NewEndTimestamp(uint256 endTimestamp);
	event TokensWithdrawn(uint256 amount);

	constructor(
		address _usdc,
		uint256 _endTimestamp,
		uint256 _maxClaimAmount,
		address _signatureStorage
	) Ownable(msg.sender) {
		usdc = IERC20(_usdc);
		endTimestamp = _endTimestamp;
		MAXIMUM_AMOUNT_TO_CLAIM = _maxClaimAmount;
		signatureStorage = ISignatureStorage(_signatureStorage);
	}

	function claim(uint256 amount, bytes32[] calldata merkleProof) external whenNotPaused nonReentrant {
		if (!isMerkleRootSet) revert("Airdrop: Merkle root not set");
		if (amount > MAXIMUM_AMOUNT_TO_CLAIM) revert("Airdrop: Amount too high");
		if (block.timestamp > endTimestamp) revert("Airdrop: Too late to claim");
		if (hasClaimed[msg.sender]) revert("Airdrop: Already claimed");
		if (!signatureStorage.hasSigned(msg.sender)) revert("Airdrop: Signature required");

		bytes32 leaf = keccak256(bytes.concat(keccak256(abi.encode(msg.sender, amount))));

		if (!MerkleProof.verify(merkleProof, merkleRoot, leaf)) revert("Airdrop: Invalid proof");

		hasClaimed[msg.sender] = true;
		usdc.safeTransfer(msg.sender, amount);

		emit Claimed(msg.sender, amount);
	}

	function canClaim(address user, uint256 amount, bytes32[] calldata merkleProof) external view returns (bool) {
		if (!signatureStorage.hasSigned(msg.sender)) {
			return false;
		}
		if (block.timestamp <= endTimestamp && !hasClaimed[user]) {
			bytes32 leaf = keccak256(bytes.concat(keccak256(abi.encode(user, amount))));
			return MerkleProof.verify(merkleProof, merkleRoot, leaf);
		} else {
			return false;
		}
	}

	function setMerkleRoot(bytes32 _merkleRoot) external onlyOwner {
		if (isMerkleRootSet) revert("Owner: Merkle root already set");
		isMerkleRootSet = true;
		merkleRoot = _merkleRoot;
		emit MerkleRootSet(_merkleRoot);
	}

	function isActive() public view returns (bool) {
		return block.timestamp < endTimestamp;
	}

	function updateEndTimestamp(uint256 _newEndTimestamp) external onlyOwner {
		endTimestamp = _newEndTimestamp;
		emit NewEndTimestamp(_newEndTimestamp);
	}

	function setSignatureStorage(address _signatureStorage) external onlyOwner {
		signatureStorage = ISignatureStorage(_signatureStorage);
	}

	function withdrawTokenRewards(uint256 _amount) external onlyOwner whenPaused {
		usdc.safeTransfer(owner(), _amount);
		emit TokensWithdrawn(_amount);
	}

	function pauseAirdrop() external onlyOwner whenNotPaused {
		_pause();
	}

	function unpauseAirdrop() external onlyOwner whenPaused {
		_unpause();
	}
}
