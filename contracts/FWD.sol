// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Snapshot.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract FWDToken is ERC20Snapshot, Ownable {
    uint256 constant INITIAL_SUPPLY = 10 ether; // PLACEHOLDER

    mapping(address => bool) public allowedToSnapshot;

    event SetSnapshotAuthorization(address _user, bool _status);

    constructor() ERC20("FWD", "FWD") {
        _mint(owner(), INITIAL_SUPPLY);
    }

    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }

    function setSnapshotAuthorization(address _user, bool _status) external onlyOwner {
        allowedToSnapshot[_user] = _status;
        emit SetSnapshotAuthorization(_user, _status);
    }

    function snapshot() external returns (uint256) {
        require(allowedToSnapshot[msg.sender], "Only allowed sender can snapshot");
        return _snapshot();
    }

    function getCurrentSnapshotId() external view returns (uint256) {
        return _getCurrentSnapshotId();
    }
}
