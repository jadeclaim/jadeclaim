// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.7;

interface IMintableERC20 {
    function mint(address, uint256) external;

    function burn(address,uint256) external;
    function setVault(address) external returns(bool);
    function owner() external view returns(address);
    function balanceOf(address) external view returns(uint256);
}
