
// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

interface IBond {
    struct Bond {
        uint256 payout; // OHM remaining to be paid
        uint256 vesting; // Blocks left to vest
        uint256 lastBlock; // Last interaction
        uint256 pricePaid; // In DAI, for front end viewing
    }
    function bondInfo(address) external view returns(Bond memory);
    function getBondsBought(address) external view returns(uint256, uint256, uint256, uint256);
    function getAllBondedPerYear() external view returns(uint256, uint256, uint256, uint256);
    function getAllHonoredPayoutsFor(address) external view returns(uint256, uint256, uint256, uint256);
}
