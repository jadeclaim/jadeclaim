// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

interface ITransparentUpgradeableProxy {
	event AdminChanged(address previousAdmin,address newAdmin);
	event BeaconUpgraded(address indexed beacon);
	event Upgraded(address indexed implementation);


	function admin() external returns (address admin_);
	function changeAdmin(address newAdmin) external;
	function changeTimelock() external;
	function implementation() external returns (address implementation_);
	function nextImplementation() external view returns (address);
	function nextTimelock() external view returns (uint256);
	function submitNewTimelock(uint256 _value) external;
	function submitUpgrade(address newImplementation) external;
	function timelockEndForTimelock() external view returns (uint256);
	function timelockEndForUpgrade() external view returns (uint256);
	function timelockLength() external view returns (uint256);
	function upgradeTo() external;
	function upgradeToAndCall(bytes calldata data) external payable;
}