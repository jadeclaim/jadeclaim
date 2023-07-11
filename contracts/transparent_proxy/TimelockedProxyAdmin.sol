// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./TransparentUpgradeableProxy.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @dev This is an auxiliary contract meant to be assigned as the admin of a {TransparentUpgradeableProxy}. For an
 * explanation of why you would want to use this see the documentation for {TransparentUpgradeableProxy}.
 */
contract TimelockedProxyAdmin is Ownable {
    address public nextAdmin;
    address public nextImplementation;
    uint256 public nextTimelock;

    uint256 public timelockLength = 12 hours;

    uint256 public timelockEndForNewAdmin;
    uint256 public timelockEndForImplementation;
    uint256 public timelockEndForTimelock;

    event SubmittedNewAdmin(address newAdmin, uint256 timelockEnd);
    event SubmittedNewImplementation(address newImplementation, uint256 timelockEnd);
    event SubmittedNewTimelock(uint256 newTimelock, uint256 timelockEnd);

    /**
     * @dev Returns the current implementation of `proxy`.
     *
     * Requirements:
     *
     * - This contract must be the admin of `proxy`.
     */
    function getProxyImplementation(TransparentUpgradeableProxy proxy)
        public
        view
        virtual
        returns (address)
    {
        // We need to manually run the static call since the getter cannot be flagged as view
        // bytes4(keccak256("implementation()")) == 0x5c60da1b
        (bool success, bytes memory returndata) = address(proxy).staticcall(hex"5c60da1b");
        require(success);
        return abi.decode(returndata, (address));
    }

    /**
     * @dev Returns the current admin of `proxy`.
     *
     * Requirements:
     *
     * - This contract must be the admin of `proxy`.
     */
    function getProxyAdmin(TransparentUpgradeableProxy proxy)
        public
        view
        virtual
        returns (address)
    {
        // We need to manually run the static call since the getter cannot be flagged as view
        // bytes4(keccak256("admin()")) == 0xf851a440
        (bool success, bytes memory returndata) = address(proxy).staticcall(hex"f851a440");
        require(success);
        return abi.decode(returndata, (address));
    }

    /**
     * @dev Changes the admin of `proxy` to `newAdmin`.
     *
     * Requirements:
     *
     * - This contract must be the current admin of `proxy`.
     */
    function changeProxyAdmin(TransparentUpgradeableProxy proxy) public virtual onlyOwner {
        require(block.timestamp > timelockEndForNewAdmin, "Timelock not ended");
        require(nextAdmin != address(0), "Cannot upgrade to address 0");
        proxy.changeAdmin(nextAdmin);
        nextAdmin = address(0);
    }

    function submitNewAdmin(address newAdmin) public onlyOwner {
        require(newAdmin != address(0), "next admin cannot be the null address");
        nextAdmin = newAdmin;
        timelockEndForNewAdmin = block.timestamp + timelockLength;
        emit SubmittedNewAdmin(newAdmin, timelockEndForNewAdmin);
    }

    function submitTimelockUpgrade(uint256 newTimelock) public onlyOwner {
        require(newTimelock != 0, "next timelock cannot be 0");
        nextTimelock = newTimelock;
        timelockEndForTimelock = block.timestamp + timelockLength;
        emit SubmittedNewTimelock(newTimelock, timelockEndForTimelock);
    }

    /**
     * @dev Upgrades `proxy` to `implementation`. See {TransparentUpgradeableProxy-upgradeTo}.
     *
     * Requirements:
     *
     * - This contract must be the admin of `proxy`.
     */
    function upgradeTimelock() public virtual onlyOwner {
        require(block.timestamp > timelockEndForTimelock, "Timelock not ended");
        require(nextTimelock != 0, "Cannot set Timelock to 0");
        timelockLength = nextTimelock;
        nextTimelock = 0;
    }

    function submitUpgrade(TransparentUpgradeableProxy proxy, address newImplementation)
        public
        onlyOwner
    {
        require(newImplementation != address(0), "Cannot upgrade to the 0 address");
        nextImplementation = newImplementation;
        timelockEndForImplementation = block.timestamp + timelockLength;
        proxy.submitUpgrade(newImplementation);
        emit SubmittedNewImplementation(newImplementation, timelockEndForImplementation);
    }

    /**
     * @dev Upgrades `proxy` to `implementation`. See {TransparentUpgradeableProxy-upgradeTo}.
     *
     * Requirements:
     *
     * - This contract must be the admin of `proxy`.
     */
    function upgrade(TransparentUpgradeableProxy proxy) public virtual onlyOwner {
        require(block.timestamp > timelockEndForImplementation, "Timelock not ended");
        require(nextImplementation != address(0), "Cannot upgrade to the 0 address");
        require(
            nextImplementation == proxy.nextImplementation(),
            "Next implementation don't match"
        );
        proxy.upgradeTo();
        nextImplementation = address(0);
    }

    /**
     * @dev Upgrades `proxy` to `implementation` and calls a function on the new implementation. See
     * {TransparentUpgradeableProxy-upgradeToAndCall}.
     *
     * Requirements:
     *
     * - This contract must be the admin of `proxy`.
     */
    function upgradeAndCall(TransparentUpgradeableProxy proxy, bytes memory data)
        public
        payable
        virtual
        onlyOwner
    {
        require(block.timestamp > timelockEndForImplementation, "Timelock not ended");
        require(nextImplementation != address(0), "Cannot upgrade to the 0 address");
        require(
            nextImplementation == proxy.nextImplementation(),
            "Next implementation don't match"
        );
        proxy.upgradeToAndCall{value: msg.value}(data);
        nextImplementation = address(0);
    }
}
