import random
from abc import ABC, abstractmethod
from typing import Callable, Optional

from brownie import web3

from . import merkle


def main():
    import pandas as pd

    df = pd.read_csv("./airdrop.csv")
    values = {row[1]: row[2] for row in df.values}
    leaves = [
        merkle.LeafData(i, account, amount) for i, (account, amount) in enumerate(values.items())
    ][:11]
    leaves.sort(key=lambda x: x.hex_value)
    for i in range(len(leaves)):
        leaves[i].index = i
    tree = merkle.StandardMerkleTree(leaves)
    leaf = tree.leaves[0]
    proof = tree.get_proof(0)
    # print(tree.hash)
    print("\n".join(tree.data))
    print("QQQQQQQQQQQQQQQQQ")
    print("\n".join(proof))
    print(tree.test_proof(leaf.hex_value, proof))
    return
    i = 0
    l = 11
    while i < l:
        print(tree.data[2 * i + 2])
        i = 2 * i + 1

    print(proof)
    # tree = merkle.MerkleTree(leaves)
    # leaf = leaves[0]
    # print(leaf.hex_value, merkle.kekkak(leaf.hex_value), merkle.kekkak(merkle.kekkak(leaf.hex_value)))
    #
    # # print([l.hex_value for l in leaves[:10]])
    # # print([l.pure_leaf() for l in leaves[:10]])
    # # print([l for l in leaves[:10]])
    # print(tree.hash)
    #
    # print(max(len(tree.get_proof(i)) for i in range(len(leaves))))
    # print(tree.dump())


main()

# import json
# # values = {get_random_address(): random.randint(0, 10**22) for _ in range(0, 5)}
# # json.dump(values, open("values.json", "w"))
# values = json.load(open("values.json", "r"))
# leaves = [LeafData(i, account, amount) for i, (account, amount) in enumerate(values.items())]
# tree = MerkleTree(leaves, kekkak)
# tree.get_proof(0)
