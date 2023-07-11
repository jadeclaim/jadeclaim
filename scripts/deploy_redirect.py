import json
import random

import pandas as pd
import pytest
from brownie import (ClaimRedirectionStorage, MerkleAirdrop, MintableERC20,
                     SignatureStorage, accounts, interface, web3)


def main():
    owner = accounts.load("jade", "jade")
    owner_params = {"from": owner, "nonce": 498}
    # print(hash)
    # return
    storage = ClaimRedirectionStorage.deploy(owner_params, publish_source=True)
    j = ClaimRedirectionStorage.get_verification_info()
    json.dump(j["standard_json_input"], open("./std.json", "w"))
