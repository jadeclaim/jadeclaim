import json
import random

import pandas as pd
from brownie import (
    MerkleAirdrop,
    MintableERC20,
    MultiMerkleAirdrop,
    Wei,
    accounts,
    web3,
)
from py_vector.common.merkle import LeafData, StandardMerkleTree, keccak
from py_vector.common.network.gas_strategies import get_snowtrace_strategy

TEST_SIZE = 1000


def get_random_address():
    characters = [str(i) for i in list(range(0, 10)) + ["A", "B", "C", "D", "E", "F"]]
    return web3.toChecksumAddress(
        "0x" + "".join([random.choice(characters) for _ in range(0, 40)])
    )


def generate_fake_data():
    values = {get_random_address(): random.randint(0, 10**22) for _ in range(0, TEST_SIZE)}
    return [LeafData(i, account, amount) for i, (account, amount) in enumerate(values.items())]


def generate_fake_csv():
    import pandas as pd

    data = [
        {"address": get_random_address(), "value": random.randint(0, 10**22)}
        for _ in range(0, TEST_SIZE)
    ]
    data += [{"address": "0x361041A2609c9deFE2A0DC99ed3E1bC0220D92Ac", "value": Wei("42 ether")}]
    data += [{"address": "0x02d0369f908dc5ff918a6b8242d87334903aa3d8", "value": Wei("42 ether")}]
    df = pd.DataFrame(data)
    df.to_csv("./airdrop.csv")


TREE_NUM = 3


def main():
    # get_snowtrace_strategy()
    # generate_fake_csv()
    df = pd.read_csv("./airdrop.csv")
    values = [
        {"address": row[1], "value": row[2], "index": idx} for idx, row in enumerate(df.values)
    ]
    admin = accounts.load("deploy_mag", "mag")
    leaves = [LeafData(data["index"], data["address"], data["value"]) for data in values]
    merkle_tree = StandardMerkleTree(leaves)
    json.dump(merkle_tree.data, open("./data.json", "w"))
    print(values)
    print([l.hex_value for l in leaves])
    return
    ind = merkle_tree.get_leaf_index_by_leaf(leaves[-2])

    leaf = leaves[-2]
    print(leaf.hex_value)
    h1 = keccak(leaf.hex_value)
    print(h1)
    print(keccak(h1))
    return

    print(leaf)
    print(ind)
    print(merkle_tree.hash)

    proof = merkle_tree.get_proof(ind)
    json.dump(merkle_tree.data, open("a.json", "w"))
    assert MultiMerkleAirdrop[-1].testProof(0, leaf.account, leaf.amount, proof)
    return
    airdrop = MultiMerkleAirdrop.deploy({"from": admin})
    print(f"airdrop {airdrop}")
    tokens = [MintableERC20.deploy("Token", "TKN", {"from": admin}) for _ in range(TREE_NUM)]
    for token in tokens:
        token.mint(airdrop, 10**32, {"from": admin})
        airdrop.addAirdrop(merkle_tree.hash, token, True, {"from": admin})

    json.dump(values, open("./airdrop.json", "w"))
