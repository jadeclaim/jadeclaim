import random

import pandas as pd
import pytest
from brownie import (MerkleAirdrop, MintableERC20, SignatureStorage, accounts,
                     interface, reverts, web3)
from py_vector.common.merkle import LeafData, MerkleTree, StandardMerkleTree

SAFE = "0x48752A9e64B6Ca04064E53941f3Dae0299319a00"

safe_sig = "0xf78e97488c79656d2ffd11cc404a6c60b5a7ab7ce06db1c8523d642fbad1936a57ef5b2a508d0e2a1fa59795f48095a17938ee45b578ef6fbe1a5431e2bacd3c1b94c83e5418b965fb555ed8ab5062ce5e54145186b7596305d3c7255e8ea38be933b691e0a0883182b9ef275d0db1ce8c56f73d5882ea636136460e5cd61ee6c01b"

redeem_amount = 12345
disclaimer = "By signing this transaction, you acknowledge that you have read, understand and accept the Disclaimer. You further acknowledge that you are voluntarily terminating your ownership and control of your Jade and/or sJade tokens, and you expressly waive and release all claims, liabilities, causes of action or damages against the Jade DAO and its agents, advisors, directors, officers, employees and any other affiliated parties or individuals arising from or relating to your ownership of the tokens and/or your participation in the DAO. Smart contract transactions execute and settle automatically, and this transaction cannot be reversed once initiated. You understand that you are entering into this transaction at your own risk."


@pytest.fixture(scope="module", autouse=True)
def safe():
    return interface.IGnosis(SAFE)


@pytest.fixture(scope="module", autouse=True)
def owner1():
    return accounts.load("jade", "jade")


@pytest.fixture(scope="module", autouse=True)
def msg(owner1):
    m = "lapin"
    return owner1.sign_defunct_message(m)


@pytest.fixture(scope="module", autouse=True)
def storage(owner1, msg):
    msg_hash = msg.messageHash.hex()
    return SignatureStorage.deploy(msg_hash, {"from": owner1})


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
def airdrop(token, storage):
    return MerkleAirdrop.deploy(token, storage, {"from": accounts[0]})


@pytest.fixture(scope="module")
def leaves(owner1):
    values = {
        get_random_address(): random.randint(0, 10**22) for _ in range(0, TEST_SIZE)
    }
    import pandas as pd

    # df = pd.read_csv("./airdrop.csv")
    # values = {row[1]: row[2] for row in df.values}
    values[owner1.address] = redeem_amount
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


def test_main():
    safe = interface.IGnosis(SAFE)
    owner1 = accounts.load("jade", "jade")
    msg = "lapin"
    msg = owner1.sign_defunct_message(msg)
    print(len(safe_sig))
    msg_hash = msg.messageHash.hex()
    print(msg_hash)
    storage = SignatureStorage.deploy(msg_hash, {"from": owner1})
    assert safe.isValidSignature(msg_hash, safe_sig)
    # print(storage.checkGnosis2(msg_hash, safe_sig, safe, {"from": owner1}))
    assert not storage.checkSignature(msg_hash, "0x11", safe, {"from": owner1})
    assert not storage.checkSignature(
        msg_hash, msg.messageHash.hex(), safe, {"from": owner1}
    )

    assert storage.checkSignature(msg_hash, safe_sig, safe, {"from": safe})
    assert not storage.checkSignature(
        msg_hash, msg.signature.hex(), safe, {"from": safe}
    )
    assert storage.checkSignature(msg_hash, msg.signature.hex(), owner1, {"from": safe})
    assert not storage.hasSigned(safe)
    storage.submitSignature(msg_hash, safe_sig, {"from": safe})
    assert storage.hasSigned(safe)


def test_all_verify(token, airdrop, tree, leaves, owner1):
    for index, leaf in enumerate(tree.leaves[: TEST_SIZE // 10]):
        proof = tree.get_proof(index)
        assert airdrop.testProof(
            leaf.account, leaf.amount, proof, {"from": accounts[0]}
        )


def test_merkle(token, airdrop, tree, leaves, storage, owner1, msg):
    for index, leaf in enumerate(tree.leaves[: TEST_SIZE // 10]):
        if leaf.account == owner1:
            continue
        proof = tree.get_proof(index)
        with reverts("user has not signed"):
            airdrop.claim(leaf.account, leaf.amount, proof, {"from": accounts[0]})
        assert token.balanceOf(leaf.account) == 0
    index, leaf = [
        (index, leaf)
        for index, leaf in enumerate(tree.leaves)
        if leaf.account == owner1
    ][0]
    msg_hash = msg.messageHash.hex()

    proof = tree.get_proof(index)
    with reverts():
        airdrop.claim(leaf.account, leaf.amount, proof, {"from": accounts[0]})
    storage.submitSignature(msg_hash, msg.signature.hex(), {"from": owner1})


def test_scoop(airdrop, owner1, token):
    b = token.balanceOf(airdrop)
    assert b > 0
    real_owner = accounts[0]
    b2 = token.balanceOf(real_owner)
    with reverts():
        airdrop.scoopTokens(token, {"from": owner1})
    airdrop.scoopTokens(token, {"from": real_owner})
    assert token.balanceOf(real_owner) == b2 + b
    assert token.balanceOf(airdrop) == 0


def test_string(storage, owner1):
    string = disclaimer
    storage.setDisclaimer(string, {"from": owner1})
    assert storage.disclaimer() == string
