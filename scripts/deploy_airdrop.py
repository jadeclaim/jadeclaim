import json
import random

import pandas as pd
import pytest
from brownie import (MerkleAirdrop, MintableERC20, SignatureStorage, accounts,
                     interface, web3)
from brownie.network.account import keccak
from py_vector.common.merkle import LeafData, MerkleTree, StandardMerkleTree


def main():
    owner = accounts.load("jade", "jade")
    owner_params = {"from": owner}
    storage = "0xB692Bbf63d5F3dd495Fd5D84E93709e268c1a29A"
    usdc = interface.IERC20("0xaf88d065e77c8cc2239327c5edb3a432268e5831")
    hash = "0x29e6b01841622c134a1a613e32e89f684284c0aa684a02aba848a36de16d91dc"

    # airdrop = MerkleAirdrop.deploy(usdc, storage, owner_params, publish_source=False)
    airdrop = MerkleAirdrop[-1]
    print(airdrop.signatureStorage())
    # airdrop.setRoot(hash, owner_params)
