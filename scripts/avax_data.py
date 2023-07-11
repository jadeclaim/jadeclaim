import json
import os
from pathlib import Path

import brownie
from brownie import Contract, Wei, accounts, interface
from tqdm import tqdm

from . import *

BATCH_SIZE = 100
transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

create_stream_topic = (
    "0x7b01d409597969366dc268d7f957a990d1ca3d3449baf8fb45db67351aecfe78"
)
airdrop_register_sign = ["0xb6f28d07"]
MULTICALL = "0x6e219eb5856388a28Fa8BD2311dedF8B4194422D"

BONDS = [
    "0xf41E19fE47D63C7F6ec20722aF749D1aC625815D",
    "0xab47ded800cee16950ab70f6063d0fe199a4c488",
    "0xDcbB8a0FE62aE5064Bd36379eEe594Cc9861A384",
]
AIRDROPS = ["0xef874e86acca337ec2e744babd40d2b17ce5898e"]


jade = "0x80B010450fDAf6a3f8dF033Ee296E92751D603B3"
lp_address = "0x8DEF3929FDa2332b523488c0b4dDDeEa7553dB6f"
sablier = "0x73f503fad13203c87889c3d5c567550b2d41d7a4"
staking = "0x273673f62198744c31129f6353f5bbd5b1d01ec0"
sJade = "0x3D9eAB723df76808bB84c05b20De27A2e69EF293"


base_path = Path("./data/avax")
scrapped_path = base_path / "scrapped"
balances_path = base_path / "balances"
log_path = base_path / "log.txt"
os.makedirs(balances_path, exist_ok=True)
os.makedirs(scrapped_path, exist_ok=True)
api_result = json.load(open("./getJadeHolders.json", "r"))
json.dump(
    list(
        set(
            [
                row["ADDRESS"][:42]
                for row in api_result.values()
                if "snap" not in row["ADDRESS"]
            ]
        )
    ),
    open("./holders.json", "w"),
)


def print_and_log(content):
    with open(log_path, "a") as f:
        f.write(content + "\n")
    print(content)


def get_jade():
    return interface.IERC20(jade)


def write_all_stakings():
    evs = get_all_events_for_account(sJade, transfer_topic)
    # print(len(evs))
    save(evs, scrapped_path, "staking", staking)


def process_staking():
    sJade_contract = Contract.from_explorer(sJade)
    evs = load(scrapped_path, "staking", staking)
    # evs = json.load(open(f"./staking_avax.json", "r"))
    users = list({"0x" + event["topics"][2][-40:] for event in evs})
    balances = {}
    for user in tqdm(users):
        balances[user] = sJade_contract.balanceOf(user, block_identifier=SNAP_HEIGHT)
    save(balances, balances_path, "staking", staking)
    jade = get_jade()
    current_jade = jade.balanceOf(staking, block_identifier=SNAP_HEIGHT)
    computed_jade = sum(balances.values())
    print_and_log(
        f"Staking : total {computed_jade}, in contract {current_jade}. DELTA= {current_jade - computed_jade}"
    )


def write_all_sablier_streams():
    evs = get_all_events_for_account(sablier, create_stream_topic)
    evs = [event for event in evs if jade[2:].lower() in event["data"]]
    # print(len(evs))
    save(evs, scrapped_path, "sablier", sablier)


def process_stream_creations_sablier():
    evs = load(scrapped_path, "sablier", sablier)
    sablier_contract = Contract.from_explorer(sablier)
    ids = [int(e["topics"][1], 16) for e in evs]
    # print(ids)

    balances = {}
    for id in ids:
        try:
            values = sablier_contract.getStream(id, block_identifier=SNAP_HEIGHT)
        except Exception as e:
            # a = "sablier streams no longer exist, so removing these log messages"
            # print(e)
            # print(id)
            continue
        balances[values[0]] = sablier_contract.balanceOf(
            id, values[0], block_identifier=SNAP_HEIGHT
        ) + balances.get(values[0], 0)
        balances[values[1]] = sablier_contract.balanceOf(
            id, values[1], block_identifier=SNAP_HEIGHT
        ) + balances.get(values[1], 0)
    save(balances, balances_path, "sablier", sablier)
    # print(sum(balances.values()))
    jade = get_jade()
    current_jade = jade.balanceOf(sablier, block_identifier=SNAP_HEIGHT)
    computed_jade = sum(balances.values())
    print_and_log(
        f"Sablier : total {computed_jade}, in contract {current_jade}. DELTA= {current_jade - computed_jade}"
    )
    return


def do_sablier():
    write_all_sablier_streams()
    time.sleep(2)
    process_stream_creations_sablier()


def write_all_interactors_with_airdrop(airdrop_address):
    txs = get_all_tx_for_account(airdrop_address)
    save(txs, scrapped_path, "airdrop", airdrop_address)


def write_all_interactors_with_bond(bond_address):
    txs = get_all_tx_for_account(bond_address)
    save(txs, scrapped_path, "bond", bond_address)


def process_airdrop_dump(airdrop):
    txs = load(scrapped_path, "airdrop", airdrop)
    creation_txs = [
        row for row in txs if row["input"][:10].lower() in airdrop_register_sign
    ]
    # print(len(creation_txs))
    claim_txs = [row for row in txs if row["input"][:10] == "0x379607f5"]
    balances = {}
    received_tokens_tx = get_all_events_for_account(
        jade, transfer_topic, topic2=addr_to_topic(airdrop)
    )
    # print(received_tokens_tx)

    for row in creation_txs:
        raw = row["input"]
        raw = raw[10:]
        begining_addresses = 2 * int(raw[64 : 64 * 2], 16)
        begining_amounts = 2 * int(raw[64 * 2 : 64 * 3], 16)
        addresses = raw[begining_addresses:begining_amounts]
        amounts = raw[begining_amounts:]
        # print(addresses[:64])
        # print(amounts[:64])
        assert addresses[:64] == amounts[:64]
        # print(addresses[:64])
        # print(int(addresses[:64], 16))

        assert len(addresses) % 64 == 0
        for i in range(64, len(addresses), 64):
            address = addresses[i : i + 64]
            amount = amounts[i : i + 64]
            balances[hex_to_addr(address)] = int(amount, 16)
    initial_balances = sum(balances.values())
    print("####################", sum(balances.values()))

    claimed = {}
    for row in claim_txs:
        if row["isError"] != "0":
            continue
        addr = row["from"]
        assert addr in balances, addr
        claimed[addr] = 1
    balances = {key: val for key, val in balances.items() if key not in claimed}
    save(balances, balances_path, "airdrop", airdrop)
    received_amount = sum(int(r["data"], 16) for r in received_tokens_tx)
    # print(f"RECEIVED on airdrop {received_amount}")
    current_jade = get_jade().balanceOf(airdrop, block_identifier=SNAP_HEIGHT)

    delta = received_amount - initial_balances - current_jade + sum(balances.values())

    print_and_log(
        f"Airdrop {airdrop} : still allocated {sum(balances.values())}, in contract {current_jade}\n"
        f"init allocation {initial_balances}, filled initially {received_amount} DELTA={delta}"
    )
    return balances, received_amount, initial_balances


def do_staking():
    write_all_stakings()
    time.sleep(2)
    process_staking()


def do_airdrops():
    for airdrop in AIRDROPS:
        write_all_interactors_with_airdrop(airdrop)

        b, received_amount, total_set = process_airdrop_dump(airdrop)
        claimed = total_set - sum(b.values())
        balance = interface.IERC20(jade).balanceOf(
            airdrop, block_identifier=SNAP_HEIGHT
        )
        distributed = received_amount - balance
        not_allocated = received_amount - total_set
        print(f"{airdrop} : {sum(b.values())/10**9}")
        print(
            f""" {claimed=}
            {distributed=}
            {balance=}
            {not_allocated=}
            """
        )


def do_holders():
    jade = get_jade()
    init_index = 0
    users = json.load(open("holders.json", "r"))
    balances = {}
    for index in tqdm(range(init_index, len(users), BATCH_SIZE)):
        with brownie.multicall(MULTICALL, SNAP_HEIGHT):
            b = {
                users[i]: jade.balanceOf(users[i])
                for i in range(index, min(index + BATCH_SIZE, len(users)))
            }
        for u, val in b.items():
            balances[u] = val + balances.get(u, 0)
        # balances.update(b)
        save(balances, balances_path, "holders", jade)

    save(balances, balances_path, "holders", jade)
    current_jade = jade.totalSupply(block_identifier=SNAP_HEIGHT)
    computed_jade = sum(balances.values())
    print_and_log(
        f"JADE : total {computed_jade}, queried {current_jade}. DELTA= {current_jade - computed_jade}"
    )

    return balances


def do_bonds():
    for bond in BONDS:
        do_bond(bond)


def do_bond(bond):
    write_all_interactors_with_bond(bond)
    txs = load(scrapped_path, "bond", bond)
    contract = interface.IBond(bond)
    users = list({row["from"] for row in txs})
    balances = {}
    init_index = len(balances)
    BATCH_SIZE = 100
    for index in tqdm(range(init_index, len(users), BATCH_SIZE)):
        with brownie.multicall(MULTICALL, SNAP_HEIGHT):
            b = {
                users[i]: sum(contract.getBondsBought(users[i]))
                - sum(contract.getAllHonoredPayoutsFor(users[i]))
                for i in range(index, min(index + BATCH_SIZE, len(users)))
            }
        for u, val in b.items():
            balances[u] = val + balances.get(u, 0)
        save(balances, balances_path, "bond", bond)
    save(balances, balances_path, "bond", bond)
    jade = get_jade()
    current_jade = jade.balanceOf(bond, block_identifier=SNAP_HEIGHT)
    computed_jade = sum(balances.values())
    print_and_log(
        f"Bond {bond} : total {computed_jade}, in contract {current_jade}. DELTA= {current_jade - computed_jade}"
    )


def write_all_interactors_with_lp():
    txs = get_all_events_for_account(lp_address, transfer_topic)
    # print(len(txs))
    save(txs, scrapped_path, "lp", lp_address)


def process_lps():
    b = process_lp_dump2()
    computed_jade = sum(b.values())
    current_jade = get_jade().balanceOf(lp_address, block_identifier=SNAP_HEIGHT)
    print_and_log(
        f"Lp {lp_address} : total {computed_jade}, in contract {current_jade}. DELTA= {current_jade - computed_jade}"
    )
    save(b, balances_path, "lp", lp_address)


def do_lp():
    write_all_interactors_with_lp()
    time.sleep(2)
    process_lps()


def dump_to_user_set_for_lp(dump):
    return set(hex_to_addr(row["topics"][2]) for row in dump)


def process_lp_dump2():
    users: list = list(dump_to_user_set_for_lp(load(scrapped_path, "lp", lp_address)))
    balances = {}
    token = interface.IJoePair(lp_address)
    BATCH_SIZE = 100
    for index in tqdm(range(0, len(users), BATCH_SIZE)):
        with brownie.multicall(MULTICALL, SNAP_HEIGHT):
            b = {
                users[i]: token.balanceOf(users[i])
                for i in range(index, min(index + BATCH_SIZE, len(users)))
            }
        balances.update(b)
    # print(sum(balances.values()))
    total_jade = interface.IERC20(jade).balanceOf(
        lp_address, block_identifier=SNAP_HEIGHT
    )
    total_lp = token.totalSupply(block_identifier=SNAP_HEIGHT)
    return {key: amount * total_jade / total_lp for key, amount in balances.items()}


def main():
    print("Collecting AVAX holders/balances")
    do_holders()

    time.sleep(4)
    print("Collecting bonds")
    do_bonds()

    time.sleep(4)
    print("Collecting staking")
    do_staking()

    time.sleep(4)
    print("Collecting airdrops")
    do_airdrops()

    time.sleep(4)
    print("Collecting sablier feeds")
    do_sablier()

    time.sleep(4)
    print("Collecting lps")
    do_lp()
