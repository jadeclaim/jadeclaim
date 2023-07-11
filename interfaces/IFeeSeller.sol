// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

interface IFeeSeller {
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    function USDC() external view returns (address);

    function WAVAX() external view returns (address);

    function addToken(address asset) external;

    function authorizedTarget(address) external view returns (bool);

    function isRegistered(address) external view returns (bool);

    function owner() external view returns (address);

    function receiver() external view returns (address);

    function renounceOwnership() external;

    function sellAllTokens(address targetToken) external;

    function sellAllTokensToUSDC() external;

    function sellTokens(address[] calldata tokensToSell, address targetToken) external;

    function sellableTokensLength() external view returns (uint256);

    function sendAllTokens() external;

    function sendTokens(address[] calldata tokensToSend) external;

    function setReceiver(address _receiver) external;

    function setSkipToken(address asset, bool skip) external;

    function setSwapHelper(address _swapHelper) external;

    function setTargetAuthorization(address _asset, bool _status) external;

    function skipToken(address) external view returns (bool);

    function swapHelper() external view returns (address);

    function tokens(uint256) external view returns (address);

    function transferOwnership(address newOwner) external;
}
