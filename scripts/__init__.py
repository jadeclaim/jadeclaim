import json
import os
import sys
import time

import requests
from brownie import chain, network
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

hex_to_addr = lambda x: "0x" + x[-40:]
addr_to_topic = lambda x: "0x" + x[-40:].zfill(64)

API_KEY = None
BASE_URL = None

if "avax" in " ".join(sys.argv):
    API_KEY = os.environ.get("SNOWTRACE_TOKEN")
    BASE_URL = "https://api.snowtrace.io/api"
    SNAP_HEIGHT = 36373925
    # print("TRUE")
elif "arbi" in " ".join(sys.argv):
    API_KEY = os.environ.get("ARBISCAN_TOKEN")
    BASE_URL = "https://api.arbiscan.io/api"
    SNAP_HEIGHT = 999999999
else:
    API_KEY = os.environ.get("BSCSCAN_TOKEN")
    BASE_URL = "https://api.bscscan.com/api"
    SNAP_HEIGHT = 32549851


def load(b, k, a):
    return json.load(open(get_final_name(b, k, a), "r"))


def save(j, b, k, a):
    json.dump(j, open(get_final_name(b, k, a), "w"))


def get_final_name(base, key, addr):
    addr = getattr(addr, "address", addr)
    return base / f"{key}_{addr}.json"


def get_paginated_event_request(
    address,
    topic0=None,
    topic1=None,
    topic2=None,
    offset=10000,
    startblock=1,
    endblock=SNAP_HEIGHT,
    sort="asc",
):
    api_key = API_KEY  # SNOWTRACE_TOKEN or "NN8PS81Y1D596ZRNK6M4SVD6VBCY893YD2"
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
    # print(url)

    return requests.get(url).json()


def get_all_events_for_account(
    address,
    topic0,
    topic1=None,
    topic2=None,
    offset=10000,
    startblock=1,
    endblock=SNAP_HEIGHT,
    sleep_time=0.5,
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

    # print(startblock - endblock)

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
        # print(tx_page)
        if tx_page["status"] == "0":
            break
        rows = tx_page["result"]
        # print(len(rows), last_block_fully_covered, len(all_tx))
        all_tx += rows
        # print(all_tx)
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
    time.sleep(sleep_time)
    # print("OOOOOOOOOOOOOOOO")
    # print(all_tx)
    all_tx = [tx for tx in all_tx if int(tx["blockNumber"], 16) <= endblock]
    # print(all_tx)
    return all_tx


def get_url_for_tx(
    address, page, page_size=30, startblock=1, endblock=SNAP_HEIGHT, sort="asc"
):
    return f"{BASE_URL}?module=account&action=txlist&address={address}&startblock={startblock}&endblock={endblock}&page={page}&offset={page_size}&sort={sort}&apikey={API_KEY}"


def get_page_tx_for_account(
    address, page, page_size=30, startblock=1, endblock=SNAP_HEIGHT, sort="asc"
):
    return requests.get(
        get_url_for_tx(address, page, page_size, startblock, endblock, sort)
    ).json()


def get_all_tx_for_account(
    address, offset=10000, start_block=1, endblock=SNAP_HEIGHT, sleep_time=0.25
):
    all_tx = []
    MAX_TX_IN_QUERY = 10000
    current_page = 1
    max_page = MAX_TX_IN_QUERY // offset
    # print(max_page)
    while True:
        # print(current_page)
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
        if len(blocks_on_last_page) == 1 and len(rows) < offset:
            last_block_fully_covered = sorted(blocks_on_last_page)[-1]
        if current_page == max_page:
            current_page = 0
            start_block = last_block_fully_covered + 1
            all_tx = [tx for tx in all_tx if int(tx["blockNumber"]) < start_block]
        current_page += 1
        time.sleep(sleep_time)
        # print(last_block_fully_covered)
    time.sleep(sleep_time)
    all_tx = [tx for tx in all_tx if int(tx["blockNumber"]) <= endblock]
    return all_tx


# def get_sources_of(address, url_getter, only_implementation=True):
#     res = requests.get(url_getter(address))
#     data = json.loads(res.text)["result"][0]
#     if data["Proxy"] != "0" and only_implementation:
#         return get_sources_of(data["Implementation"])
#
#     sources_str = data["SourceCode"]
#     sources_str = sources_str.replace("\r\n", "")[1:-1]
#     return {
#         key: val["content"] for key, val in json.loads(sources_str)["sources"].items()
#     }
