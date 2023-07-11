import json
import os

import brownie
from brownie import Wei, accounts, interface
from tqdm import tqdm

from . import *

BATCH_SIZE = 100

MULTICALL = "0x571Aa1B3369B54cC28bF3836db284982D9239CA7"
WRITE_BONDS = True
PROCESS_BONDS = True

LPS = ["0x46503d91D7a41FCbDC250E84ceE9D457d082D7b4"]
BONDS = [
    "0xb855ee49de8f05a441104c4e053a3be7ff45ae56",
    "0x266a93EA88C002ff223E81E40300056289938142",
    "0xD6C73ef5e71A350f8AE642C01Aad3d7637a0c1C8",
]
AIRDROPS = [
    "0x84bccd98ae46b14cb6ce645b43a5ef970160a114",
    "0xb8e3729c9d337782703105e164254e5b9acb780b",
    "0xa9abfb5e0f79e3f20e7305d8d1fe8faa9cc70e56",
    "0x0c41afa1b92b5c5ae50ef51d9c14e587a69304bc",
    "0x124374a7ffb5195fc6d9ceedce5007658641a393",
]
stake_func_signature = "0xa694fc3a"

staking = "0x097d72e1D9bbb8d0263477f9b20bEBF66f243AF4"
staking_helper = "0xA50dCCc889F41998d3343D0b73493b64c22a6dDc"
advisors_gnosis = "0x4d8f3b540e76ac57ee34cbcd9c44cac4ea9aa285"
vesting = "0xf5bce5077908a1b7370b9ae04adc565ebd643966"

transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
bond_created_topic = (
    "0x1fec6dc81f140574bf43f6b1e420ae1dd47928b9d57db8cbd7b8611063b85ae5"
)
create_stream_topic = (
    "0x1a2d760a604c03eaa74e64c0e42f0e4f41824be534853f4c2f3ed42d36fed25c"
)
airdrop_register_sign = "0x1cb81303"


furo = "0x4ab2fc6e258a0ca7175d05ff10c5cf798a672cae"

jade = "0x7ad7242A99F21aa543F9650A56D141C57e4F6081"
sJade = "0x94cea04c51e7d3ec0a4a97ac0c3b3c9254c2ad41"

addr = "0x1b462629d6608354bc1a7f67f3d4a58105ab2534"

from pathlib import Path

base_path = Path("./data/bsc")
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


def get_path(key, addr):
    return get_final_name(base_path, key, addr)


def write_all_furo_streams():
    evs = get_all_events_for_account(furo, create_stream_topic)
    evs = [event for event in evs if jade[2:].lower() in event["data"]]
    # print(len(evs))
    save(evs, scrapped_path, "furo", furo)


def process_stream_creations_furo():
    evs = load(scrapped_path, "furo", furo)
    furo_contract = Contract.from_explorer(furo)
    ids = [int(e["topics"][1], 16) for e in evs]
    ids_to_data = {}
    ids_to_owner = {}
    for id in tqdm(ids):
        ids_to_data[id] = furo_contract.streamBalanceOf(
            id, block_identifier=SNAP_HEIGHT
        )
        ids_to_owner[id] = furo_contract.ownerOf(id, block_identifier=SNAP_HEIGHT)
    # print(ids_to_data)
    data = {"balances": ids_to_data, "owners": ids_to_owner}
    save(data, balances_path, "furo", furo_contract)
    return data


def do_furo():
    # print("start")
    write_all_furo_streams()
    b = process_stream_creations_furo()
    total_computed = sum([a + b for a, b in b["balances"].values()])
    current_balance = get_jade().balanceOf(vesting, block_identifier=SNAP_HEIGHT)
    delta = total_computed - current_balance
    print_and_log(f"Furo : {total_computed}, balance {current_balance}, DELTA={delta}")


def write_all_interactors_with_sJade():
    txs = get_all_events_for_account(sJade, transfer_topic)
    save(txs, scrapped_path, "sJade", sJade)


def write_all_interactors_with_lp(lp_address):
    txs = get_all_events_for_account(lp_address, transfer_topic)
    save(txs, scrapped_path, "lp", lp_address)


def write_all_interactors_with_airdrop(airdrop_address):
    txs = get_all_tx_for_account(airdrop_address)
    save(txs, scrapped_path, "airdrop", airdrop_address)


def write_all_interactors_with_bond(bond_address):
    txs = get_all_tx_for_account(bond_address)
    save(txs, scrapped_path, "bond", bond_address)


def write_all_interactors_with_staking():
    txs = get_all_tx_for_account(staking)
    # print(len(txs))
    txs += get_all_tx_for_account(staking_helper)
    save(txs, scrapped_path, "staking", staking)


from brownie import Contract

# ev = get_all_events_for_account(
#     jade,
#     transfer_topic,
#     topic1=None,
#     topic2=addr_to_topic(bond),
#     offset=10000,
#     startblock=1,
#     endblock=99999999,
#     sleep_time=0.5,
# )
# ev = json.load(open("f.json", "r"))
# print({r["topics"][1] for r in ev})
# return


# write_all_interactors_with_sJade()
# return
#


def do_holders():
    jade = get_jade()
    init_index = 0
    users = json.load(open("holders.json", "r"))
    users = list({u for u in users if u.lower()})
    balances = {}
    for index in tqdm(range(init_index, len(users), BATCH_SIZE)):
        time.sleep(2)
        with brownie.multicall(MULTICALL, SNAP_HEIGHT):
            b = {
                users[i]: jade.balanceOf(users[i])
                for i in range(index, min(index + BATCH_SIZE, len(users)))
            }
        for u, val in b.items():
            balances[u] = val + balances.get(u, 0)
        # balances.update(b)
        save(balances, balances_path, "jade", jade)

    save(balances, balances_path, "jade", jade)
    current_jade = jade.totalSupply(block_identifier=SNAP_HEIGHT)
    computed_jade = sum(balances.values())
    print_and_log(
        f"JADE : total {computed_jade}, queried {current_jade}. DELTA= {current_jade - computed_jade}"
    )

    return balances


# def do_holders():
#     jade = get_jade()
#     init_index = 0
#     users = json.load(open("holders.json", "r"))
#     users = [u for u in users if u.lower() != staking.lower()]
#     balances = {}
#     for user in tqdm(users):
#         balances[user] = jade.balanceOf(user)
#
#     save(balances, balances_path, "jade", jade)
#     current_jade = jade.totalSupply()
#     computed_jade = sum(balances.values())
#     print_and_log(
#         f"JADE : total {computed_jade}, queried {current_jade}. DELTA= {current_jade - computed_jade}"
#     )
#
#     return balances


def do_staking():
    # write_all_interactors_with_staking()
    b = process_staking_dump(staking)
    b = load(balances_path, "staking", staking)
    # print("staking", sum(b.values()) / 1e9)
    computed_jade = sum(b.values())
    current_jade = get_jade().balanceOf(staking, block_identifier=SNAP_HEIGHT)
    print_and_log(
        f"Staking {staking} : total {computed_jade}, in contract {current_jade}. DELTA= {current_jade - computed_jade}"
    )


def do_bonds_bsc():
    for bond in BONDS:
        if WRITE_BONDS:
            write_all_interactors_with_bond(bond)
    for bond in BONDS:
        if PROCESS_BONDS:
            b = process_bond_dump(bond)
            computed_jade = sum(b.values())
            current_jade = interface.IERC20(jade).balanceOf(
                bond, block_identifier=SNAP_HEIGHT
            )
            delta = computed_jade - current_jade
            print_and_log(
                f"BOND {bond} : total {computed_jade}, in contract {current_jade}. DELTA= {delta}"
            )


def do_airdrops():
    for airdrop in AIRDROPS:
        write_all_interactors_with_airdrop(airdrop)
        time.sleep(5)
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


def do_lps():
    for lp_address in LPS:
        write_all_interactors_with_lp(lp_address)

        b = process_lp_dump2(lp_address)
        save(b, balances_path, "lp", lp_address)

        computed_jade = sum(b.values())
        current_jade = interface.IERC20(jade).balanceOf(
            lp_address, block_identifier=SNAP_HEIGHT
        )
        delta = computed_jade - current_jade
        print_and_log(
            f"LP : total {computed_jade}, in contract {current_jade}. DELTA= {current_jade - computed_jade}"
        )


def dump_to_user_set_for_lp(dump):
    return set(hex_to_addr(row["topics"][2]) for row in dump)


def dump_to_user_set_for_bond(dump):
    res = []
    for row in dump:
        # print(row["functionName"])

        if "deposit" in row["functionName"]:
            res.append("0x" + row["input"][-40:])
            # print(res[-1])
        else:
            # print("Issue")
            res.append("0x" + row["from"][-40:])
    return list(set([r.lower() for r in res]))


def process_bond_dump(bond_address):
    j = load(scrapped_path, "bond", bond_address)

    # print("LENGTH IS", len(j))
    users = dump_to_user_set_for_bond(j)
    try:
        balances = load(balances_path, "bond", bond_address)
        print("LOADED")
    except FileNotFoundError:
        balances = {}
    bond = interface.IBond(bond_address)
    # bond = Contract.from_explorer(bond_address)
    for user in tqdm(users):
        if user in balances:
            continue
        balances[user] = bond.bondInfo(user, block_identifier=SNAP_HEIGHT)[0]
        if len(balances) % 100 == 0:
            save(balances, balances_path, "bond", bond_address)
    save(balances, balances_path, "bond", bond_address)
    return balances


def process_bond_dump(bond_address):
    users = dump_to_user_set_for_bond(load(scrapped_path, "bond", bond_address))
    try:
        balances = load(balances_path, "bond", bond_address)
        print("LOADED")
    except FileNotFoundError:
        balances = {}
    bond = interface.IBond(bond_address)
    # bond = Contract.from_explorer(bond_address)
    init_index = len(balances)
    # print(init_index, len(users), BATCH_SIZE)
    for index in tqdm(range(init_index, len(users), BATCH_SIZE)):
        with brownie.multicall(MULTICALL, SNAP_HEIGHT):
            b = {
                users[i]: bond.bondInfo(users[i])[0]
                for i in range(index, min(index + BATCH_SIZE, len(users)))
            }
        for u, val in b.items():
            balances[u] = val + balances.get(u, 0)
        # balances.update(b)
        save(balances, balances_path, "bond", bond_address)

    save(balances, balances_path, "bond", bond_address)
    return balances


def process_lp_dump(lp_address):
    users = dump_to_user_set_for_lp(load(scrapped_path, "lp", lp_address))
    balances = {}
    token = interface.IJoePair(lp_address)
    for user in tqdm(users):
        balances[user] = token.balanceOf(user, block_identifier=SNAP_HEIGHT)
    return balances


def process_lp_dump2(lp_address):
    users: list = list(dump_to_user_set_for_lp(load(scrapped_path, "lp", lp_address)))
    print("start lp process")
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
        print(index)
    total_jade = interface.IERC20(jade).balanceOf(
        lp_address, block_identifier=SNAP_HEIGHT
    )
    total_lp = token.totalSupply(block_identifier=SNAP_HEIGHT)
    return {key: amount * total_jade // total_lp for key, amount in balances.items()}


def process_staking_dump(staking):
    users = json.load(open("holders.json", "r"))
    users = [u for u in users if u.lower() != staking.lower()]
    balances = {}
    sToken = interface.IERC20(sJade)
    BATCH_SIZE = 100
    init_index = 0
    # print(init_index, len(users), BATCH_SIZE)
    for index in tqdm(range(init_index, len(users), BATCH_SIZE)):
        with brownie.multicall(MULTICALL, SNAP_HEIGHT):
            b = {
                users[i]: sToken.balanceOf(users[i])
                for i in range(index, min(index + BATCH_SIZE, len(users)))
            }
        for u, val in b.items():
            balances[u] = val + balances.get(u, 0)
        # balances.update(b)
    save(balances, balances_path, "staking", staking)


# def process_staking_dump(staking):
#     users = json.load(open("holders.json", "r"))
#     users = [u for u in users if u.lower() != staking.lower()]
#     if os.path.isfile(get_final_name(balances_path, "staking", staking)):
#         balances = load(balances_path, "staking", staking)
#     else:
#         balances = {}
#     sToken = interface.IERC20(sJade)
#     BATCH_SIZE = 100
#     init_index = 0
#     # print(init_index, len(users), BATCH_SIZE)
#     users = [u for u in users if u not in balances]
#     i = 0
#     for user in tqdm(users):
#         i += 1
#         if user in balances:
#             continue
#         balances[user] = sToken.balanceOf(user)
#         if i % BATCH_SIZE == 0:
#             save(balances, balances_path, "staking", staking)
#     save(balances, balances_path, "staking", staking)


def process_airdrop_dump(airdrop):
    txs = load(scrapped_path, "airdrop", airdrop)
    creation_txs = [row for row in txs if row["input"][:10] == airdrop_register_sign]
    # print(len(creation_txs))
    claim_txs = [row for row in txs if row["input"][:10] == "0x5b88349d"]
    balances = {}
    received_tokens_tx = get_all_events_for_account(
        jade, transfer_topic, topic2=addr_to_topic(airdrop)
    )
    # print(received_tokens_tx)

    for row in creation_txs:
        raw = row["input"]
        raw = raw[10:]
        begining_addresses = 2 * int(raw[:64], 16)
        begining_amounts = 2 * int(raw[64 : 64 + 64], 16)
        addresses = raw[begining_addresses:begining_amounts]
        amounts = raw[begining_amounts:]
        assert addresses[:64] == amounts[:64]
        # print(addresses[:64])
        # print(int(addresses[:64], 16))

        assert len(addresses) % 64 == 0
        for i in range(64, len(addresses), 64):
            address = addresses[i : i + 64]
            amount = amounts[i : i + 64]
            balances[hex_to_addr(address)] = int(amount, 16)
    initial_balances = sum(balances.values())
    # print("####################", sum(balances.values()))

    claimed = {}
    for row in claim_txs:
        if row["isError"] != "0":
            continue
        addr = row["from"]
        assert addr in balances, addr
        claimed[addr] = 1
    balances = {key: val for key, val in balances.items() if key not in claimed}
    received_amount = sum(int(r["data"], 16) for r in received_tokens_tx)
    # print(f"RECEIVED on airdrop {received_amount}")
    current_jade = get_jade().balanceOf(airdrop, block_identifier=SNAP_HEIGHT)

    delta = received_amount - initial_balances - current_jade + sum(balances.values())

    save(balances, balances_path, "airdrop", airdrop)
    print_and_log(
        f"Airdrop {airdrop} : still allocated {sum(balances.values())}, in contract {current_jade}\n"
        f"init allocation {initial_balances}, filled initially {received_amount} DELTA={delta}"
    )
    return balances, received_amount, initial_balances


# main()
def main():
    print("Collecting LP")
    do_lps()

    print("Collecting holders")
    do_holders()

    print("Collecting sJade")
    do_staking()

    print("Collecting furo")
    do_furo()

    print("Collecting bonds")
    do_bonds_bsc()
    
    print("Collecting airdrops")
    do_airdrops()
