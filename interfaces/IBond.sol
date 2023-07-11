
// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

interface IBond {
    struct Bond {
        uint payout; // OHM remaining to be paid
        uint vesting; // Blocks left to vest
        uint lastBlock; // Last interaction
        uint pricePaid; // In DAI, for front end viewing
    }
    function bondInfo(address) external view returns(Bond memory);
}
