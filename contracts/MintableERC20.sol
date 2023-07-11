// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts v4.4.1 (token/ERC20/ERC20.sol)
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

// IS HERE FOR TESTING PURPOSES

contract MintableERC20 is ERC20, Ownable {
    /*
    The ERC20 deployed will be owned by the others contracts of the protocol, specifically by
    Masterchief and MainStaking, forbidding the misuse of these functions for nefarious purposes
    */
    mapping(address => bool) public isSupplyManager;
    uint8 private decimals_;

    constructor(
        string memory name_,
        string memory symbol_,
        uint8 _decimals
    ) ERC20(name_, symbol_) {
        decimals_ = _decimals;
    }

    function toggleSupplyManager(address user) external onlyOwner {
        isSupplyManager[user] = !isSupplyManager[user];
    }

    function mint(address account, uint256 amount) external virtual {
        require(isSupplyManager[msg.sender] || msg.sender == owner(), "Only supply manager");
        _mint(account, amount);
    }

    function decimals() public view override returns (uint8) {
        return decimals_;
    }

    function burn(address account, uint256 amount) external virtual {
        require(isSupplyManager[msg.sender] || msg.sender == owner(), "Only supply manager");
        _burn(account, amount);
    }
}
