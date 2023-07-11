import json
import random

import pandas as pd
import pytest
from brownie import (MerkleAirdrop, MintableERC20, SignatureStorage, accounts,
                     interface, web3)
from brownie.network.account import keccak
from py_vector.common.merkle import LeafData, MerkleTree, StandardMerkleTree

disclaimer = "By signing this transaction, you acknowledge that you have read, understand and accept the Disclaimer. You further acknowledge that you are voluntarily terminating your ownership and control of your Jade and/or sJade tokens, and you expressly waive and release all claims, liabilities, causes of action or damages against the Jade DAO and its agents, advisors, directors, officers, employees and any other affiliated parties or individuals arising from or relating to your ownership of the tokens and/or your participation in the DAO. Smart contract transactions execute and settle automatically, and this transaction cannot be reversed once initiated. You understand that you are entering into this transaction at your own risk."


def main():
    owner = accounts.load("jade", "jade")
    owner_params = {"from": owner}
    # print(hash)
    # return
    disc_final = f"\x19Ethereum Signed Message:\n{len(disclaimer)}{disclaimer}"
    hash = keccak(text=disc_final).hex()
    print(hash)
    # c.setHash(hash, owner_params)

    storage = SignatureStorage.deploy(hash, owner_params, publish_source=False)
    storage.setDisclaimer(disclaimer, owner_params)
    j = SignatureStorage.get_verification_info()
    json.dump(j["standard_json_input"], open("./std.json", "w"))
    storage.checkSignature(
        hash,
        "0xd56eca73548e61db766712021df9609402164de60319f37ac331e77d04915b944e48c0a693ea12d08e2617cc6ba25c03f6ecb0cf518b80ab45d8439d3e8674211b",
        # storage,
        "0x361041a2609c9defe2a0dc99ed3e1bc0220d92ac",
    )
