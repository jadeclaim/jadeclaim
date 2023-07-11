// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.7;

import "@openzeppelin/contracts/access/Ownable.sol";

contract ClaimRedirectionStorage is Ownable {
    mapping(address => address) public redirectTo;

    event Redirection(address indexed owner, address indexed destination);

    function redirect(address destination) external {
        redirectTo[msg.sender] = destination;
        emit Redirection(msg.sender, destination);
    }
}
