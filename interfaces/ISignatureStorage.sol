// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.7;


interface ISignatureStorage {
    function hasSigned(address) external returns (bool) ;
}
