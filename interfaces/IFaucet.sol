// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

interface IFaucet {
    function multiClaim() external;

    function registerToken(address tokenAddress) external;

    function update() external;
}
