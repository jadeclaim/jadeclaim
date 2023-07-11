// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.7;

import "@openzeppelinUpgradeable/contracts/proxy/utils/Initializable.sol";
import "@openzeppelinUpgradeable/contracts/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../interfaces/IMintableERC20.sol";

contract TokenStaking is Initializable, OwnableUpgradeable {
    using SafeERC20 for IERC20;

    address public Token;
    address public sToken;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);

    function __TokenStaking_init(address _Token, address _sToken) public initializer {
        __Ownable_init();
        require(_Token != address(0));
        Token = _Token;
        require(_sToken != address(0));
        sToken = _sToken;
    }

    /**
        @notice stake FWD
        @param _amount uint
        @return bool
     */
    function stake(uint256 _amount, address _recipient) external returns (bool) {
        IERC20(Token).safeTransferFrom(msg.sender, address(this), _amount);
        IMintableERC20(sToken).mint(_recipient, _amount);
        emit Staked(msg.sender, _amount);
    }

    function unstake(uint256 _amount) external {
        IMintableERC20(sToken).burn(msg.sender, _amount);
        IERC20(Token).safeTransfer(msg.sender, _amount);
        emit Unstaked(msg.sender, _amount);
    }

    /**
        @notice returns contract FWD holdings, including bonuses provided
        @return uint
     */
    function contractBalance() public view returns (uint256) {
        return IERC20(Token).balanceOf(address(this));
    }
}
