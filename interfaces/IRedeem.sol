// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

interface IRedeem {
	event OwnershipTransferred(address indexed previousOwner,address indexed newOwner);
	event Redeemed(address indexed user,uint256 tokenQty,uint256 usdQty);
	event SetBurnVault(address newWallet);
	event SetBurnWallet(address newWallet);
	event SetTokenPrice(uint256 price,uint256 decimals);
	event SetVaultPct(uint256 pct);


	function PCT_PRECISION() external view returns (uint256);
	function __Redeem_init(address _token, address _stable, address _burnWallet, address _burnVault, uint256 _price) external;
	function burnVault() external view returns (address);
	function burnWallet() external view returns (address);
	function owner() external view returns (address);
	function priceDecimals() external view returns (uint256);
	function redeemToken(uint256 amountToRedeem, uint256 slippage) external;
	function renounceOwnership() external;
	function scoopTokens(address _token, uint256 amount) external;
	function setBurnVault(address vault) external;
	function setBurnWallet(address wallet) external;
	function setTokenPrice(uint256 price, uint256 decimals) external;
	function setVaultPct(uint256 pct) external;
	function stable() external view returns (address);
	function stableDecimals() external view returns (uint256);
	function token() external view returns (address);
	function tokenDecimals() external view returns (uint256);
	function tokenPriceInUsd() external view returns (uint256);
	function transferOwnership(address newOwner) external;
	function vaultPct() external view returns (uint256);
}