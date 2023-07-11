// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Snapshot.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract sFWDToken is ERC20Snapshot, Ownable {
    constructor() ERC20("sFWD", "sFWD") {}

    function mint(address _recipient, uint256 _amount) external onlyOwner {
        _mint(_recipient, _amount);
    }

    function burn(address _recipient, uint256 _amount) external onlyOwner {
        _burn(_recipient, _amount);
    }
}
