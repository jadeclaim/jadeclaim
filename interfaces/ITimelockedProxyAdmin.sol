// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

interface ITimelockedProxyAdmin {
	event OwnershipTransferred(address indexed previousOwner,address indexed newOwner);
	event SubmittedNewAdmin(address newAdmin,uint256 timelockEnd);
	event SubmittedNewImplementation(address newImplementation,uint256 timelockEnd);
	event SubmittedNewTimelock(uint256 newTimelock,uint256 timelockEnd);


	function changeProxyAdmin(address proxy) external;
	function getProxyAdmin(address proxy) external view returns (address);
	function getProxyImplementation(address proxy) external view returns (address);
	function nextAdmin() external view returns (address);
	function nextImplementation() external view returns (address);
	function nextTimelock() external view returns (uint256);
	function owner() external view returns (address);
	function renounceOwnership() external;
	function submitNewAdmin(address newAdmin) external;
	function submitTimelockUpgrade(uint256 newTimelock) external;
	function submitUpgrade(address proxy, address newImplementation) external;
	function timelockEndForImplementation() external view returns (uint256);
	function timelockEndForNewAdmin() external view returns (uint256);
	function timelockEndForTimelock() external view returns (uint256);
	function timelockLength() external view returns (uint256);
	function transferOwnership(address newOwner) external;
	function upgrade(address proxy) external;
	function upgradeAndCall(address proxy, bytes calldata data) external payable;
	function upgradeTimelock() external;
}