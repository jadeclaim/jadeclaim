// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Snapshot.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract FWDToken is ERC20Snapshot, Ownable {
    uint256 constant MAX_SUPPLY = 10 ether; // PLACEHOLDER

    mapping(address => bool) allowedToSnapshot;

    event SetSnapshotAuthorization(address _user, bool _status);

    constructor() ERC20("FWD", "FWD") {
        _mint(owner(), MAX_SUPPLY);
    }

    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }

    function setSnapshotAuthorization(address _user, bool _status) external onlyOwner {
        allowedToSnapshot[_user] = _status;
        emit SetSnapshotAuthorization(_user, _status);
    }
}
