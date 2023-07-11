// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract Airdrop {
    using SafeERC20 for IERC20;

    address token;
    mapping(address => uint256) public amounts;

    constructor(address _token) {
        token = _token;
    }

    function setAmounts(address[] calldata _addresses, uint256[] calldata _amounts) external {
        uint256 length = _addresses.length;
        for (uint256 i = 0; i < length; i++)
            // IERC20(token).safeTransfer(_addresses[i],_amounts[i]);
            amounts[_addresses[i]] = _amounts[i];
    }
}
