//SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract MultiMerkleAirdrop is Ownable {
    using SafeERC20 for IERC20;
    uint256 public airdropNextIndex;
    // This is a packed array of booleans.
    mapping(uint256 => bytes32) public roots;

    // This event is triggered whenever a call to #claim succeeds.
    mapping(uint256 => mapping(address => bool)) public claimedAddresses;

    mapping(uint256 => IERC20) public tokens;
    mapping(uint256 => uint256) public claimedAmounts;
    mapping(uint256 => bool) isAirdropSetUp;
    mapping(address => address) addressRedirection;

    event Claimed(uint256 airdropIndex, address account, uint256 amount);
    event CreatedAirdrop(uint256 airdropIndex, address token);

    struct ClaimData {
        uint256 index;
        address account;
        uint256 amount;
        bytes32[] proof;
    }

    constructor() {}

    function setRedirection(address user, address redirectTo) external onlyOwner {
        addressRedirection[user] = redirectTo;
    }

    function addAirdrop(
        bytes32 root,
        IERC20 token,
        bool setReady
    ) external onlyOwner returns (uint256) {
        tokens[airdropNextIndex] = token;
        roots[airdropNextIndex] = root;
        isAirdropSetUp[airdropNextIndex] = setReady;
        airdropNextIndex++;
        emit CreatedAirdrop(airdropNextIndex - 1, address(token));
        return airdropNextIndex - 1;
    }

    function testProof(
        uint256 airdropIndex,
        address account,
        uint256 amount,
        bytes32[] calldata merkleProof
    ) public view returns (bool) {
        bytes32 node = keccak256(bytes.concat(keccak256(abi.encode(account, amount))));
        return MerkleProof.verify(merkleProof, roots[airdropIndex], node);
    }

    function setAirdropStatus(uint256 airdropIndex, bool airdropStatus) external onlyOwner {
        isAirdropSetUp[airdropIndex] = airdropStatus;
    }

    function claimedAirdropsForUser(address user) public view returns (bool[] memory) {
        bool[] memory claimed = new bool[](airdropNextIndex);
        for (uint256 index; index < airdropNextIndex; index++) {
            claimed[index] = claimedAddresses[index][user];
        }
        return claimed;
    }

    function claim(
        uint256 airdropIndex,
        address account,
        uint256 amount,
        bytes32[] calldata merkleProof
    ) public {
        // Verify the merkle proof.
        // bytes32 node = keccak256(abi.encodePacked(account, amount));
        bytes32 node = keccak256(bytes.concat(keccak256(abi.encode(account, amount))));
        require(isAirdropSetUp[airdropIndex], "Airdrop not started yet");
        require(!claimedAddresses[airdropIndex][account], "Drop already claimed.");
        require(MerkleProof.verify(merkleProof, roots[airdropIndex], node), "Invalid proof.");

        // Mark it claimed and send the token.
        claimedAddresses[airdropIndex][account] = true;
        address recipient = account;
        if (addressRedirection[account] != address(0)) {
            recipient = addressRedirection[account];
        }
        tokens[airdropIndex].safeTransfer(recipient, amount);
        claimedAmounts[airdropIndex] += amount;

        emit Claimed(airdropIndex, account, amount);
    }

    function setRoot(uint256 airdropIndex, bytes32 _root) external onlyOwner {
        require(!isAirdropSetUp[airdropIndex], "Airdrop has started");
        roots[airdropIndex] = _root;
    }

    function pullTokens(IERC20 token, uint256 amount) external onlyOwner {
        token.safeTransfer(msg.sender, amount);
    }

    function multiClaim(ClaimData[] calldata claims) external {
        uint256 length = claims.length;
        for (uint256 array_index; array_index < length; ++array_index) {
            claim(
                claims[array_index].index,
                claims[array_index].account,
                claims[array_index].amount,
                claims[array_index].proof
            );
        }
    }
}
