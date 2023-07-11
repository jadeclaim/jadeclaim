import json

import brownie
from brownie import Wei, accounts, interface
from tqdm import tqdm

# from py_vector.common.scraping import *
#


LPS = ["0x46503d91D7a41FCbDC250E84ceE9D457d082D7b4"]
BONDS = ["0x266a93EA88C002ff223E81E40300056289938142"]
AIRDROPS = [
    "0x84bccd98ae46b14cb6ce645b43a5ef970160a114",
    "0xb8e3729c9d337782703105e164254e5b9acb780b",
    "0xa9abfb5e0f79e3f20e7305d8d1fe8faa9cc70e56",
    "0x0c41afa1b92b5c5ae50ef51d9c14e587a69304bc",
    "0x124374a7ffb5195fc6d9ceedce5007658641a393",
]


transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
bond_created_topic = (
    "0x1fec6dc81f140574bf43f6b1e420ae1dd47928b9d57db8cbd7b8611063b85ae5"
)
airdrop_register_sign = "0x1cb81303"


def write_all_interactors_with_sJade():
    txs = get_all_events_for_account(sJade, transfer_topic)
    json.dump(txs, open(f"./transfers{sJade}.json", "w"))


def write_all_interactors_with_lp(lp_address):
    txs = get_all_events_for_account(lp_address, transfer_topic)
    json.dump(txs, open(f"./transfers{lp_address}.json", "w"))


def write_all_interactors_with_airdrop(airdrop_address):
    txs = get_all_tx_for_account(airdrop_address)
    json.dump(txs, open(f"airdrops{airdrop_address}.json", "w"))


def write_all_interactors_with_bond(bond_address):
    txs = get_all_tx_for_account(bond_address)
    json.dump(txs, open(f"./bonds{bond_address}.json", "w"))


jade = "0x7ad7242A99F21aa543F9650A56D141C57e4F6081"
sJade = "0x94cea04c51e7d3ec0a4a97ac0c3b3c9254c2ad41"


def main():
    # for bond in BONDS:
    #     process_bond_dump2(bond)
    # write_all_interactors_with_bond(bond)
    write_all_interactors_with_sJade()
    # for airdrop in AIRDROPS:
    #     write_all_interactors_with_airdrop(airdrop)
    # process_airdrop_dump(airdrop)

    # write_all_interactors_with_lp(lp_address)
    # json.load(open(f"./transfers{lp_address}.json", "r"))
    # process_lp_dump2(lp_address)


def dump_to_user_set_for_lp(dump):
    return set(hex_to_addr(row["topics"][2]) for row in dump)


def dump_to_user_set_for_bond(dump):
    res = []
    for row in dump:
        if "deposit" in row["functionName"]:
            res.append("0x" + row["input"][-40:])
        else:
            res.append(row["from"])
    return list(set(res))


def process_bond_dump(bond_address):
    users = dump_to_user_set_for_bond(
        json.load(open(f"./bonds{bond_address}.json", "r"))
    )
    balances = {}
    bond = interface.IBond(bond_address)
    for user in tqdm(users):
        balances[user] = bond.bondInfo(user)[0]
    return balances


def process_bond_dump2(bond_address):
    users = dump_to_user_set_for_bond(
        json.load(open(f"./bonds{bond_address}.json", "r"))
    )
    balances = {}
    bond = interface.IBond(bond_address)
    BATCH_SIZE = 100
    for index in tqdm(range(0, len(users), BATCH_SIZE)):
        with brownie.multicall:
            b = {
                users[i]: bond.bondInfo(users[i])[0]
                for i in range(index, min(index + BATCH_SIZE, len(users)))
            }
        balances.update(b)
    return balances


def process_lp_dump(lp_address):
    users = dump_to_user_set_for_lp(
        json.load(open(f"./transfers{lp_address}.json", "r"))
    )
    balances = {}
    token = interface.IJoePair(lp_address)
    for user in tqdm(users):
        balances[user] = token.balanceOf(user)
    return balances


def process_lp_dump2(lp_address):
    users: list = list(
        dump_to_user_set_for_lp(json.load(open(f"./transfers{lp_address}.json", "r")))
    )
    balances = {}
    token = interface.IJoePair(lp_address)
    BATCH_SIZE = 100
    for index in tqdm(range(0, len(users), BATCH_SIZE)):
        with brownie.multicall:
            b = {
                users[i]: token.balanceOf(users[i])
                for i in range(index, min(index + BATCH_SIZE, len(users)))
            }
        balances.update(b)
    total_jade = interface.IERC20(jade).balanceOf(lp_address)
    total_lp = token.totalSupply()
    return {key: amount * total_jade / total_lp for key, amount in balances.items()}


def process_airdrop_dump(airdrop):
    txs = json.load(open(f"./airdrops{airdrop}.json", "r"))
    creation_txs = [row for row in txs if row["input"][:10] == airdrop_register_sign]
    print(len(creation_txs))
    claim_txs = [row for row in txs if row["input"][:10] == "0x5b88349d"]
    balances = {}
    for row in creation_txs:
        raw = row["input"]
        raw = raw[10:]
        begining_addresses = 2 * int(raw[:64], 16)
        begining_amounts = 2 * int(raw[64 : 64 + 64], 16)
        addresses = raw[begining_addresses:begining_amounts]
        amounts = raw[begining_amounts:]
        assert addresses[:64] == amounts[:64]
        print(addresses[:64])
        print(int(addresses[:64], 16))

        assert len(addresses) % 64 == 0
        for i in range(64, len(addresses), 64):
            address = addresses[i : i + 64]
            amount = amounts[i : i + 64]
            balances[hex_to_addr(address)] = int(amount, 16)

    for row in claim_txs:
        if row["isError"] != "0":
            continue
        addr = row["from"]
        assert addr in balances, addr
        balances[addr] = 0
    return balances


hex_to_addr = lambda x: "0x" + x[-40:]

import json
import time

import requests
from brownie import chain

# from py_vector import SNOWTRACE_TOKEN

API_KEY = "5J437CHA2HG8CN417FBBYI2RK3F24C8WCK"
BASE_URL = "https://api.bscscan.com/api"


def get_paginated_event_request(
    address,
    topic0=None,
    topic1=None,
    topic2=None,
    offset=10000,
    startblock=1,
    endblock=99999999,
    sort="asc",
):
    api_key = API_KEY  # SNOWTRACE_TOKEN or "NN8PS81Y1D596ZRNK6M4SVD6VBCY893YD2"
    # params = {
    #     "apikey": api_key,
    #     "module": "logs",
    #     "action": "getLogs",
    #     "address": str(address),
    #     "offset": offset, "startblock": startblock, "endblock": endblock, "sort": sort}
    url = (
        f"{BASE_URL}?module=logs&action=getLogs&fromBlock={startblock}&endblock={endblock}"
        f"&offset={offset}&address={address}&apikey={api_key}&sort={sort}"
    )

    if topic0 is not None:
        url += f"&topic0={topic0}"
    if topic1 is not None:
        url += f"&topic1={topic1}"
    if topic2 is not None:
        url += f"&topic2={topic2}"

    return requests.get(url).json()


def get_all_events_for_account(
    address,
    topic0,
    topic1=None,
    topic2=None,
    offset=10000,
    startblock=1,
    endblock=99999999,
    sleep_time=0.25,
):
    if endblock is None:
        endblock = chain[-1]["number"]
    all_tx = []
    last_block_fully_covered = 1

    startblock = max(
        int(
            get_paginated_event_request(
                address, topic0, topic1=topic1, topic2=topic2, offset=1, sort="asc"
            )["result"][0]["blockNumber"],
            16,
        ),
        startblock,
    )
    endblock = min(
        int(
            requests.get(
                BASE_URL, params={"module": "proxy", "action": "eth_blockNumber"}
            ).json()["result"],
            16,
        ),
        endblock,
    )

    print(startblock - endblock)

    pbar = tqdm(total=(endblock - startblock), ncols=100)
    while True:
        previous_block = startblock
        tx_page = get_paginated_event_request(
            address,
            topic0,
            topic1=topic1,
            topic2=topic2,
            offset=offset,
            startblock=startblock,
            endblock=endblock,
        )
        if tx_page["status"] == "0":
            break
        rows = tx_page["result"]
        # print(len(rows), last_block_fully_covered, len(all_tx))
        all_tx += rows
        if len(rows) < 5:
            break
        blocks_on_last_page = list({int(row["blockNumber"], 16) for row in rows})
        if len(blocks_on_last_page) > 1:
            last_block_fully_covered = sorted(blocks_on_last_page)[-2]
            startblock = last_block_fully_covered + 1
            all_tx = [tx for tx in all_tx if int(tx["blockNumber"], 16) < startblock]
        time.sleep(sleep_time)
        pbar.update(startblock - previous_block)
        json.dump(all_tx, open("checkpoint.json", "w"))
    pbar.close()
    return all_tx


def get_url_for_tx(
    address, page, page_size=30, startblock=1, endblock=99999999, sort="asc"
):
    return f"{BASE_URL}?module=account&action=txlist&address={address}&startblock={startblock}&endblock={endblock}&page={page}&offset={page_size}&sort={sort}&apikey={API_KEY}"


def get_page_tx_for_account(
    address, page, page_size=30, startblock=1, endblock=99999999, sort="asc"
):
    return requests.get(
        get_url_for_tx(address, page, page_size, startblock, endblock, sort)
    ).json()


def get_all_tx_for_account(address, offset=3000, start_block=1, sleep_time=0.25):
    all_tx = []
    MAX_TX_IN_QUERY = 10000
    current_page = 1
    max_page = MAX_TX_IN_QUERY // offset
    while True:
        tx_page = get_page_tx_for_account(
            address, current_page, offset, startblock=start_block
        )
        if tx_page["status"] == "0":
            break
            # return all_tx
        rows = tx_page["result"]
        all_tx += rows

        blocks_on_last_page = list({int(row["blockNumber"]) for row in rows})
        if len(blocks_on_last_page) > 1:
            last_block_fully_covered = sorted(blocks_on_last_page)[-2]
        if current_page == max_page:
            current_page = 0
            start_block = last_block_fully_covered + 1
            all_tx = [tx for tx in all_tx if int(tx["blockNumber"]) < start_block]
        current_page += 1
        time.sleep(sleep_time)
    return all_tx


def get_sources_of(address, url_getter, only_implementation=True):
    res = requests.get(url_getter(address))
    data = json.loads(res.text)["result"][0]
    if data["Proxy"] != "0" and only_implementation:
        return get_sources_of(data["Implementation"])

    sources_str = data["SourceCode"]
    sources_str = sources_str.replace("\r\n", "")[1:-1]
    return {
        key: val["content"] for key, val in json.loads(sources_str)["sources"].items()
    }


# main()
