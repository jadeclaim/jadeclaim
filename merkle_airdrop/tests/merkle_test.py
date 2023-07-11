import json
import random

import pytest
from brownie import (ZERO_ADDRESS, MerkleAirdrop, MintableERC20,
                     MultiMerkleAirdrop, accounts, web3)
from py_vector.common.merkle import LeafData, MerkleTree, StandardMerkleTree

TEST_SIZE = 100


def get_random_address():
    characters = [str(i) for i in list(range(0, 10)) + ["A", "B", "C", "D", "E", "F"]]
    return web3.toChecksumAddress(
        "0x" + "".join([random.choice(characters) for _ in range(0, 40)])
    )


@pytest.fixture(scope="module")
def token():
    return MintableERC20.deploy("Token", "TKN", {"from": accounts[0]})


@pytest.fixture(scope="module")
def airdrop(token):
    return MerkleAirdrop.deploy(token, {"from": accounts[0]})


@pytest.fixture(scope="module")
def leaves():
    values = {
        get_random_address(): random.randint(0, 10**22) for _ in range(0, TEST_SIZE)
    }
    import pandas as pd

    df = pd.read_csv("./airdrop.csv")
    values = {row[1]: row[2] for row in df.values}
    return [
        LeafData(i, account, amount)
        for i, (account, amount) in enumerate(values.items())
    ]


@pytest.fixture(scope="module")
def tree(token, airdrop, leaves):
    user = accounts[0]
    merkle_tree = StandardMerkleTree(leaves)
    airdrop.setRoot(merkle_tree.hash, {"from": user})
    token.mint(airdrop, 10**32, {"from": user})
    return merkle_tree


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_merkle_offchain(token, airdrop, tree, leaves):
    print(tree.leaves[:10])
    for index, leaf in enumerate(tree.leaves[: TEST_SIZE // 100]):
        proof = tree.get_proof(index)
        assert tree.test_proof(leaf.hex_value, proof)


def test_merkle(token, airdrop, tree, leaves):
    for index, leaf in enumerate(tree.leaves[: TEST_SIZE // 10]):
        proof = tree.get_proof(index)
        airdrop.claim(leaf.account, leaf.amount, proof, {"from": accounts[0]})
        assert token.balanceOf(leaf.account) == leaf.amount


def test_all_verify(token, airdrop, tree, leaves):
    for index, leaf in enumerate(tree.leaves[: TEST_SIZE // 10]):
        proof = tree.get_proof(index)
        assert airdrop.testProof(
            leaf.account, leaf.amount, proof, {"from": accounts[0]}
        )
