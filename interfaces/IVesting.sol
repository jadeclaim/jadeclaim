// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

interface IVesting {
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    function add(address beneficiary, uint256 _amount) external;

    function available(address _user) external view returns (uint256);

    function cliffLength() external view returns (uint256);

    function owner() external view returns (address);

    function percentVested() external view returns (uint256 percent);

    function renounceOwnership() external;

    function startDate() external view returns (uint256);

    function totalAdded() external view returns (uint256);

    function transferOwnership(address newOwner) external;

    function vestingLength() external view returns (uint256);

    function withdraw() external;
}
