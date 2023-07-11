import json
import os
from pathlib import Path

from brownie import Contract, Wei, accounts, interface
from tqdm import tqdm

from . import *

## USAGE
# Set properly AIRDROP_ADDRESS, Run with brownie
# Likely :
# brownie run scripts/fetch_all_claimed.py --network arbitrum-main
# output : in the claimed.json file

AIRDROP_ADDRESS = "0x79d3c07d1be5c05D821DeDf45B6AB0d424241CA4"
OUTPUT_PATH = "./claimed.json"
topic = "0xd8138f8a3f377c5259ca548e70e4c2de94f129f5a11036a15b69513cba2b426a"
print(SNAP_HEIGHT)


def write_all_interactors_with_airdrop():
    evs = get_all_events_for_account(AIRDROP_ADDRESS, topic0=topic)
    users = list({"0x" + event["data"][26:66] for event in evs})

    return users


def main():
    users = write_all_interactors_with_airdrop()
    json.dump(users, open(OUTPUT_PATH, "w"))
