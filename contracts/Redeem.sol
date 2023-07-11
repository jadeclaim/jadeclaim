// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import "interfaces/IFWDToken.sol";

contract Redeem is Ownable {
    using SafeERC20 for IERC20;

    address public immutable token; // token is FWD, our new token
    address public immutable stable;
    uint256 public tokenPriceInUsd;
    uint256 public priceDecimals;
    uint256 public immutable tokenDecimals;
    uint256 public immutable stableDecimals;

    event SetTokenPrice(uint256 price, uint256 decimals);
    event Redeemed(address indexed user, uint256 tokenQty, uint256 usdQty);

    constructor(
        address _token,
        address _stable,
        uint256 _price
    ) {
        token = _token;
        stable = _stable;
        tokenPriceInUsd = _price;
        priceDecimals = 2;
        tokenDecimals = IERC20Metadata(_token).decimals();
        stableDecimals = IERC20Metadata(_stable).decimals();
    }

    function setTokenPrice(uint256 price, uint256 decimals) public onlyOwner {
        require(decimals <= 18, "Too much precision");
        require(
            price * 10**(18 - decimals) >= tokenPriceInUsd * 10**(18 - priceDecimals),
            "Price can no longer go down"
        );
        tokenPriceInUsd = price;
        priceDecimals = decimals;
        emit SetTokenPrice(price, decimals);
    }

    function redeemToken(uint256 amountToRedeem, uint256 slippage) public {
        uint256 stableAmount = (amountToRedeem * tokenPriceInUsd) /
            (10**priceDecimals) /
            (10**(tokenDecimals - stableDecimals));

        // require(stableAmount >= slippage, "Slippage too high");
        // Slippage is now meaningless

        IERC20(token).safeTransferFrom(msg.sender, address(this), amountToRedeem);
        IFWDToken(token).burn(amountToRedeem);
        emit Redeemed(msg.sender, amountToRedeem, stableAmount);
        IERC20(stable).safeTransfer(msg.sender, stableAmount);
    }

    function scoopTokens(address _token, uint256 amount) external onlyOwner {
        IERC20(_token).safeTransfer(msg.sender, amount);
    }
}
