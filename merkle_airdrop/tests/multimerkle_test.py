import json
import random

import pytest
from brownie import (
    ZERO_ADDRESS,
    MerkleAirdrop,
    MintableERC20,
    MultiMerkleAirdrop,
    accounts,
    interface,
    reverts,
    web3,
)
from py_vector.common.merkle import LeafData, MerkleTree, StandardMerkleTree

TEST_SIZE = 100
TREE_NUM = 5


def get_random_address():
    characters = [str(i) for i in list(range(0, 10)) + ["A", "B", "C", "D", "E", "F"]]
    return web3.toChecksumAddress(
        "0x" + "".join([random.choice(characters) for _ in range(0, 40)])
    )


def get_random_amount():
    return random.randint(1, 100) * 10**17


@pytest.fixture(scope="module")
def tokens():
    return [MintableERC20.deploy("Token", "TKN", {"from": accounts[0]}) for _ in range(TREE_NUM)]


@pytest.fixture(scope="module")
def airdrop():
    _airdrop = MultiMerkleAirdrop.deploy({"from": accounts[0]})
    return _airdrop


@pytest.fixture(scope="module")
def leaves():
    def _leaves():
        values = {get_random_address(): get_random_amount() for _ in range(0, TEST_SIZE)}
        values[accounts[-1].address] = get_random_amount()
        return [LeafData(i, account, amount) for i, (account, amount) in enumerate(values.items())]

    return [_leaves() for _ in range(TREE_NUM)]


@pytest.fixture(scope="module")
def trees(tokens, airdrop, leaves):
    def _tree(token, airdrop, leaves):
        user = accounts[0]
        merkle_tree = StandardMerkleTree(leaves)
        airdrop.addAirdrop(merkle_tree.hash, token, True, {"from": user})
        token.mint(airdrop, 10**32, {"from": user})
        return merkle_tree

    return [_tree(tokens[i], airdrop, leaves[i]) for i in range(TREE_NUM)]


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_merkle(tokens, airdrop, trees, leaves):
    for tree_index in range(TREE_NUM):
        tree = trees[tree_index]
        token = tokens[tree_index]
        for index, leaf in enumerate(tree.leaves[: TEST_SIZE // 10]):
            proof = tree.get_proof(index)
            airdrop.claim(tree_index, leaf.account, leaf.amount, proof, {"from": accounts[0]})
            assert token.balanceOf(leaf.account) == leaf.amount


def test_cannot_claim_twice(tokens, airdrop, trees, leaves):
    for tree_index in range(TREE_NUM):
        tree = trees[tree_index]
        token = tokens[tree_index]
        for index, leaf in enumerate(tree.leaves[: TEST_SIZE // 10]):
            proof = tree.get_proof(index)
            airdrop.claim(tree_index, leaf.account, leaf.amount, proof, {"from": accounts[0]})
            with reverts("Drop already claimed."):
                airdrop.claim(tree_index, leaf.account, leaf.amount, proof, {"from": accounts[0]})

            assert token.balanceOf(leaf.account) == leaf.amount


def test_airdrop_setting_up(tokens, airdrop, trees, leaves):
    tree = trees[0]
    token = tokens[0]
    proof = tree.get_proof(0)
    leaf = tree.leaves[0]
    airdrop.setAirdropStatus(0, False, {"from": accounts[0]})
    with reverts("Airdrop not started yet"):
        airdrop.claim(0, leaf.account, leaf.amount, proof, {"from": accounts[0]})
    airdrop.setAirdropStatus(0, True, {"from": accounts[0]})
    airdrop.claim(0, leaf.account, leaf.amount, proof, {"from": accounts[0]})


def test_pull_tokens(tokens, airdrop, trees, leaves):
    token = tokens[0]
    owner = accounts[0]
    bad_caller = accounts[1]
    airdrop_balance = token.balanceOf(airdrop)
    with reverts():
        airdrop.pullTokens(token, airdrop_balance, {"from": bad_caller})
    airdrop.pullTokens(token, airdrop_balance, {"from": owner})
    assert token.balanceOf(owner) == airdrop_balance


def test_multiclaim(tokens, airdrop, trees: list[StandardMerkleTree], leaves):
    claim_data = []
    account_in_all_drops = accounts[-1]
    amounts_to_check = {}
    for i in range(TREE_NUM):
        tree = trees[i]
        index, leaf = [
            (idx, leaf)
            for idx, leaf in enumerate(tree.leaves)
            if leaf.account == account_in_all_drops
        ][0]
        assert account_in_all_drops == leaf.account
        proof = tree.get_proof(index)
        claim_data.append([i, account_in_all_drops, leaf.amount, proof])
        token = airdrop.tokens(i)
        amounts_to_check[token] = amounts_to_check.get(token, 0) + leaf.amount
    airdrop.multiClaim(claim_data, {"from": account_in_all_drops})
    for token, amount in amounts_to_check.items():
        assert interface.IERC20(token).balanceOf(account_in_all_drops) == amount


def test_redirect(tokens, airdrop, trees: list[StandardMerkleTree], leaves):
    tree = trees[0]
    index = 0
    leaf = tree.leaves[index]
    redirected_to_leaf = tree.leaves[index + 1]
    redirect_to = redirected_to_leaf.account
    assert leaf.account != redirect_to
    airdrop.setRedirection(leaf.account, redirect_to, {"from": accounts[0]})
    proof = tree.get_proof(index)
    airdrop.claim(0, leaf.account, leaf.amount, proof, {"from": accounts[0]})
    with reverts():
        airdrop.claim(0, leaf.account, leaf.amount, proof, {"from": accounts[0]})
    assert not airdrop.claimedAddresses(0, redirect_to)
    assert airdrop.claimedAddresses(0, leaf.account)
    proof = tree.get_proof(index + 1)
    airdrop.claim(
        0, redirected_to_leaf.account, redirected_to_leaf.amount, proof, {"from": accounts[0]}
    )
