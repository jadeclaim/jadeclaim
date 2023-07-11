// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

// This contract is a small variant of the proxy pattern in the sense that
//timelock information is held on the proxy itself
// The rest is left unchanged

/**
 * @dev This contract implements a proxy that is upgradeable by an admin.
 *
 * To avoid https://medium.com/nomic-labs-blog/malicious-backdoors-in-ethereum-proxies-62629adf3357[proxy selector
 * clashing], which can potentially be used in an attack, this contract uses the
 * https://blog.openzeppelin.com/the-transparent-proxy-pattern/[transparent proxy pattern]. This pattern implies two
 * things that go hand in hand:
 *
 * 1. If any account other than the admin calls the proxy, the call will be forwarded to the implementation, even if
 * that call matches one of the admin functions exposed by the proxy itself.
 * 2. If the admin calls the proxy, it can access the admin functions, but its calls will never be forwarded to the
 * implementation. If the admin tries to call a function on the implementation it will fail with an error that says
 * "admin cannot fallback to proxy target".
 *
 * These properties mean that the admin account can only be used for admin actions like upgrading the proxy or changing
 * the admin, so it's best if it's a dedicated account that is not used for anything else. This will avoid headaches due
 * to sudden errors when trying to call a function from the proxy implementation.
 *
 * Our recommendation is for the dedicated account to be an instance of the {ProxyAdmin} contract. If set up this way,
 * you should think of the `ProxyAdmin` instance as the real administrative interface of your proxy.
 */
contract TransparentUpgradeableProxy is ERC1967Proxy {
    /**
     * @dev Initializes an upgradeable proxy managed by `_admin`, backed by the implementation at `_logic`, and
     * optionally initialized with `_data` as explained in {ERC1967Proxy-constructor}.
     */
    bytes32 private constant _TIMELOCK_LENGTH_SLOT =
        bytes32(uint256(keccak256("eip1967.proxy.timelockLength")) - 1);
    bytes32 private constant _TIMELOCK_END_FOR_UPGRADE_SLOT =
        bytes32(uint256(keccak256("eip1967.proxy.timelockEndForUpgrade")) - 1);
    bytes32 private constant _TIMELOCK_END_FOR_TIMELOCK_SLOT =
        bytes32(uint256(keccak256("eip1967.proxy.timelockEndForTimelock")) - 1);
    bytes32 private constant _NEXT_TIMELOCK_SLOT =
        bytes32(uint256(keccak256("eip1967.proxy.nextTimelock")) - 1);
    bytes32 private constant _NEXT_IMPLEMENTATION_SLOT =
        bytes32(uint256(keccak256("eip1967.proxy.nextImplementation")) - 1);

    function timelockLength() external view returns (uint256) {
        return StorageSlot.getUint256Slot(_TIMELOCK_LENGTH_SLOT).value;
    }

    function timelockEndForUpgrade() external view returns (uint256) {
        return StorageSlot.getUint256Slot(_TIMELOCK_END_FOR_UPGRADE_SLOT).value;
    }

    function timelockEndForTimelock() external view returns (uint256) {
        return StorageSlot.getUint256Slot(_TIMELOCK_END_FOR_TIMELOCK_SLOT).value;
    }

    function nextTimelock() external view returns (uint256) {
        return StorageSlot.getUint256Slot(_NEXT_TIMELOCK_SLOT).value;
    }

    function nextImplementation() external view returns (address) {
        return StorageSlot.getAddressSlot(_NEXT_IMPLEMENTATION_SLOT).value;
    }

    constructor(
        address _logic,
        address admin_,
        bytes memory _data
    ) payable ERC1967Proxy(_logic, _data) {
        assert(_ADMIN_SLOT == bytes32(uint256(keccak256("eip1967.proxy.admin")) - 1));
        StorageSlot.getUint256Slot(_TIMELOCK_LENGTH_SLOT).value = 1 hours;
        _changeAdmin(admin_);
    }

    /**
     * @dev Modifier used internally that will delegate the call to the implementation unless the sender is the admin.
     */
    modifier ifAdmin() {
        if (msg.sender == _getAdmin()) {
            _;
        } else {
            _fallback();
        }
    }

    /**
     * @dev Returns the current admin.
     *
     * NOTE: Only the admin can call this function. See {ProxyAdmin-getProxyAdmin}.
     *
     * TIP: To get this value clients can read directly from the storage slot shown below (specified by EIP1967) using the
     * https://eth.wiki/json-rpc/API#eth_getstorageat[`eth_getStorageAt`] RPC call.
     * `0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103`
     */
    function admin() external ifAdmin returns (address admin_) {
        admin_ = _getAdmin();
    }

    function submitNewTimelock(uint256 _value) external ifAdmin {
        StorageSlot.getUint256Slot(_NEXT_TIMELOCK_SLOT).value = _value;
        StorageSlot.getUint256Slot(_TIMELOCK_END_FOR_TIMELOCK_SLOT).value =
            block.timestamp +
            StorageSlot.getUint256Slot(_TIMELOCK_LENGTH_SLOT).value;
    }

    function changeTimelock() external ifAdmin {
        require(
            block.timestamp >= StorageSlot.getUint256Slot(_TIMELOCK_END_FOR_TIMELOCK_SLOT).value,
            "Timelock not ended"
        );
        StorageSlot.getUint256Slot(_TIMELOCK_LENGTH_SLOT).value = StorageSlot
            .getUint256Slot(_NEXT_TIMELOCK_SLOT)
            .value;
        StorageSlot.getUint256Slot(_NEXT_TIMELOCK_SLOT).value = 0;
    }

    /**
     * @dev Returns the current implementation.
     *
     * NOTE: Only the admin can call this function. See {ProxyAdmin-getProxyImplementation}.
     *
     * TIP: To get this value clients can read directly from the storage slot shown below (specified by EIP1967) using the
     * https://eth.wiki/json-rpc/API#eth_getstorageat[`eth_getStorageAt`] RPC call.
     * `0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc`
     */
    function implementation() external ifAdmin returns (address implementation_) {
        implementation_ = _implementation();
    }

    /**
     * @dev Changes the admin of the proxy.
     *
     * Emits an {AdminChanged} event.
     *
     * NOTE: Only the admin can call this function. See {ProxyAdmin-changeProxyAdmin}.
     */
    function changeAdmin(address newAdmin) external virtual ifAdmin {
        _changeAdmin(newAdmin);
    }

    function submitUpgrade(address newImplementation) external ifAdmin {
        if (StorageSlot.getUint256Slot(_TIMELOCK_LENGTH_SLOT).value == 0) {
            _upgradeToAndCall(
                StorageSlot.getAddressSlot(_NEXT_IMPLEMENTATION_SLOT).value,
                bytes(""),
                false
            );
        } else {
            StorageSlot.getAddressSlot(_NEXT_IMPLEMENTATION_SLOT).value = newImplementation;
            StorageSlot.getUint256Slot(_TIMELOCK_END_FOR_UPGRADE_SLOT).value =
                block.timestamp +
                StorageSlot.getUint256Slot(_TIMELOCK_LENGTH_SLOT).value;
        }
    }

    /**
     * @dev Upgrade the implementation of the proxy.
     *
     * NOTE: Only the admin can call this function. See {ProxyAdmin-upgrade}.
     */
    function upgradeTo() external ifAdmin {
        require(
            StorageSlot.getAddressSlot(_NEXT_IMPLEMENTATION_SLOT).value != address(0),
            "Can't upgrade to address 0"
        );
        require(
            block.timestamp > StorageSlot.getUint256Slot(_TIMELOCK_END_FOR_UPGRADE_SLOT).value,
            "Timelock not finished"
        );
        _upgradeToAndCall(
            StorageSlot.getAddressSlot(_NEXT_IMPLEMENTATION_SLOT).value,
            bytes(""),
            false
        );
        StorageSlot.getAddressSlot(_NEXT_IMPLEMENTATION_SLOT).value = address(0);
    }

    /**
     * @dev Upgrade the implementation of the proxy, and then call a function from the new implementation as specified
     * by `data`, which should be an encoded function call. This is useful to initialize new storage variables in the
     * proxied contract.
     *
     * NOTE: Only the admin can call this function. See {ProxyAdmin-upgradeAndCall}.
     */
    function upgradeToAndCall(bytes calldata data) external payable ifAdmin {
        require(
            StorageSlot.getAddressSlot(_NEXT_IMPLEMENTATION_SLOT).value != address(0),
            "Can't upgrade to address 0"
        );
        require(
            block.timestamp > StorageSlot.getUint256Slot(_TIMELOCK_END_FOR_UPGRADE_SLOT).value,
            "Timelock not finished"
        );
        _upgradeToAndCall(StorageSlot.getAddressSlot(_NEXT_IMPLEMENTATION_SLOT).value, data, true);
        StorageSlot.getAddressSlot(_NEXT_IMPLEMENTATION_SLOT).value = address(0);
    }

    /**
     * @dev Returns the current admin.
     */
    function _admin() internal view virtual returns (address) {
        return _getAdmin();
    }

    /**
     * @dev Makes sure the admin cannot access the fallback function. See {Proxy-_beforeFallback}.
     */
    function _beforeFallback() internal virtual override {
        require(
            msg.sender != _getAdmin(),
            "TransparentUpgradeableProxy: admin cannot fallback to proxy target"
        );
        super._beforeFallback();
    }
}
