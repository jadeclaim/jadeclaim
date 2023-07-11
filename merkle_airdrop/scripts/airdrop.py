import random

import pandas as pd
from brownie import MerkleAirdrop, MintableERC20, accounts, web3
from py_vector.common.merkle import LeafData, MerkleTree

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
    data += [{"address": "0x361041A2609c9deFE2A0DC99ed3E1bC0220D92Ac", "value": 4242424242}]
    data += [{"address": "0x02d0369f908dc5ff918a6b8242d87334903aa3d8", "value": 4242424242}]
    df = pd.DataFrame(data)
    df.to_csv("./airdrop.csv")


def main():
    df = pd.read_csv("./airdrop.csv")
    values = [{"address": row[1], "value": row[2]} for row in df.values]
    print(values[0])
    import json

    json.dump(values, open("./airdrop.json", "w"))
