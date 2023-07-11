// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

import "@openzeppelinUpgradeable/contracts/proxy/utils/Initializable.sol";
import "@openzeppelinUpgradeable/contracts/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import "interfaces/IFWDToken.sol";

contract Redeem is Initializable, OwnableUpgradeable {
    using SafeERC20 for IERC20;

    uint256 public constant PCT_PRECISION = 1e4;
    address public token;
    address public stable;
    uint256 public tokenPriceInUsd;
    uint256 public priceDecimals;
    uint256 public tokenDecimals;
    uint256 public stableDecimals;

    event SetTokenPrice(uint256 price, uint256 decimals);
    event Redeemed(address indexed user, uint256 tokenQty, uint256 usdQty);

    function __Redeem_init(
        address _token,
        address _stable,
        uint256 _price
    ) public initializer {
        __Ownable_init();
        token = _token;
        stable = _stable;
        tokenPriceInUsd = _price;
        priceDecimals = 2;
        tokenDecimals = IERC20Metadata(token).decimals();
        stableDecimals = IERC20Metadata(stable).decimals();
    }

    function setTokenPrice(uint256 price, uint256 decimals) public onlyOwner {
        tokenPriceInUsd = price;
        priceDecimals = decimals;
        emit SetTokenPrice(price, decimals);
    }

    function redeemToken(uint256 amountToRedeem, uint256 slippage) public {
        uint256 stableAmount = stableDecimals < tokenDecimals
            ? (amountToRedeem * tokenPriceInUsd) /
                (10**priceDecimals) /
                (10**(tokenDecimals - stableDecimals))
            : ((amountToRedeem * tokenPriceInUsd) * (10**(stableDecimals - tokenDecimals))) /
                (10**priceDecimals);
        require(stableAmount >= slippage, "Slippage too high");

        IERC20(token).safeTransferFrom(msg.sender, address(this), amountToRedeem);
        IFWDToken(token).burn(amountToRedeem);
        emit Redeemed(msg.sender, amountToRedeem, stableAmount);
        IERC20(stable).safeTransfer(msg.sender, stableAmount);
    }

    function scoopTokens(address _token, uint256 amount) external onlyOwner {
        IERC20(_token).safeTransfer(msg.sender, amount);
    }
}
