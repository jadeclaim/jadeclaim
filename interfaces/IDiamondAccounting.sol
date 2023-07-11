// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.7;

interface IDiamondAccounting {
    function getUserInfo(address user)
        external
        view
        returns (
            bool,
            uint256,
            uint256,
            uint256
        );

    function lowerRemainingJLP(address _user, uint256 _amount) external;

    function jlp() external view returns (address);
}
