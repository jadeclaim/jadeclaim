// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

interface IGnosis {
    function approveHash(bytes32 hashToApprove) external;
    function approvedHashes(address user, bytes32 hash) external view returns(uint256);
    function isValidSignature(bytes calldata _data, bytes calldata _signature) external view returns (bytes4);
    function getBondsBought(address) external view returns(uint256, uint256, uint256, uint256);
    function getAllBondedPerYear() external view returns(uint256, uint256, uint256, uint256);
    function getAllHonoredPayoutsFor(address) external view returns(uint256, uint256, uint256, uint256);
}
