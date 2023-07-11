// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

interface IFWDToken {
	event Approval(address indexed owner,address indexed spender,uint256 value);
	event OwnershipTransferred(address indexed previousOwner,address indexed newOwner);
	event Snapshot(uint256 id);
	event Transfer(address indexed from,address indexed to,uint256 value);


	function allowance(address owner, address spender) external view returns (uint256);
	function approve(address spender, uint256 amount) external returns (bool);
	function balanceOf(address account) external view returns (uint256);
	function balanceOfAt(address account, uint256 snapshotId) external view returns (uint256);
	function burn(uint256 amount) external; 
	function decimals() external view returns (uint8);
	function decreaseAllowance(address spender, uint256 subtractedValue) external returns (bool);
	function increaseAllowance(address spender, uint256 addedValue) external returns (bool);
	function name() external view returns (string memory);
	function owner() external view returns (address);
	function renounceOwnership() external;
	function symbol() external view returns (string memory);
	function totalSupply() external view returns (uint256);
	function totalSupplyAt(uint256 snapshotId) external view returns (uint256);
	function transfer(address recipient, uint256 amount) external returns (bool);
	function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
	function transferOwnership(address newOwner) external;
}
