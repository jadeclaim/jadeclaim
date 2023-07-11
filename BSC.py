# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import json

# %%
import pandas as pd

foo = lambda x: eval(x) if isinstance(x, str) else x

import os

# %%
from pathlib import Path

# %%
bsc_balances_path = Path("./data/bsc/balances")
files = [p for p in bsc_balances_path.iterdir()]

# %%
files

# %%
ignore = [
    "0x571Aa1B3369B54cC28bF3836db284982D9239CA7",
    "0x46503d91D7a41FCbDC250E84ceE9D457d082D7b4",
    "0xb855ee49de8f05a441104c4e053a3be7ff45ae56",
    "0x266a93EA88C002ff223E81E40300056289938142",
    "0xD6C73ef5e71A350f8AE642C01Aad3d7637a0c1C8",
    "0x097d72e1D9bbb8d0263477f9b20bEBF66f243AF4",
    "0xA50dCCc889F41998d3343D0b73493b64c22a6dDc",
    "0x4d8f3b540e76ac57ee34cbcd9c44cac4ea9aa285",
    "0xf5bce5077908a1b7370b9ae04adc565ebd643966",
    "0x4ab2fc6e258a0ca7175d05ff10c5cf798a672cae",
    "0x7ad7242A99F21aa543F9650A56D141C57e4F6081",
    "0x94cea04c51e7d3ec0a4a97ac0c3b3c9254c2ad41",
    "0x273673f62198744c31129f6353f5bbd5b1d01ec0",
]
ignore = [i.lower() for i in ignore]

# %%
AIRDROPS = [
    "0x84bccd98ae46b14cb6ce645b43a5ef970160a114",
    "0xb8e3729c9d337782703105e164254e5b9acb780b",
    "0xa9abfb5e0f79e3f20e7305d8d1fe8faa9cc70e56",
    "0x0c41afa1b92b5c5ae50ef51d9c14e587a69304bc",
    "0x124374a7ffb5195fc6d9ceedce5007658641a393",
]


# %%
exclude = [
    "0x78bc5ee9f11d133a08b331c2e18fe81be0ed02dc",
    "0x11a0c9270d88c99e221360bca50c2f6fda44a980",
    "0x9448e099761da0253ef2fa9296d2ba77d322e28c",
    "0x91b4c8de02c3396860d032eb987a51cb0dec56f6",
    "0xc7029e939075f48fa2d5953381660c7d01570171",
    "0x1b462629d6608354bc1a7f67f3d4a58105ab2534",
    "0x9d017bbb1e9ad1dc677307735b7c6b404e1c5c1b",
    "0x73a348ef3bbd14bdb98be1f92891582251ac4f45",
    "0x6ED562a792214AC325F2682302bD690237c6c08E",
    "0x8e9d9d3f7681dc49059d23254ec95395dd7e305d",
    "0x5ba7edc664b3c0955c317ecc8e24dd2f9f2a862e",
    "0xc6fd3b1dc606014cff8fc1e5a0c10d716dce12f3",
    "0xa50dccc889f41998d3343d0b73493b64c22a6ddc",
    "0x7ad7242A99F21aa543F9650A56D141C57e4F6081",
    "0x7ad7242A99F21aa543F9650A56D141C57e4F6081",
    "0x94cea04c51e7d3ec0a4a97ac0c3b3c9254c2ad41",
    "0x94cea04c51e7d3ec0a4a97ac0c3b3c9254c2ad41",
    "0x02944e3fb72aa13095d7cebd8389fc74bec8e48e",
    "0x097d72e1D9bbb8d0263477f9b20bEBF66f243AF4",
    "0x6f0bc6217faa5a2f503c057ee6964b756a09ae2c",
    "0xf15ff5df9924dbf0f257a79b63bf5678701af564",
    "0xd012a9c8159b0e7325448ed30b1499fdddac0f40",
    "0x489f866c0698c8d6879f5c0f527bc8281046042d",
    "0xcb0718b150552af8904e7cb1c62758dcb149b072",
    "0xaea6b4aad5e315a40afd77a1f794f61161499fa5",
    "0x169169a50d9a8fbf99edacf9aa10297e2b3c92dd",
    "0x1aa87a1554919f1537e48626eaa49cb3e967a737",
    "0x91b4c8de02c3396860d032eb987a51cb0dec56f6",
    "0x45ecfd1f5cf000a8320d8b88d53373bdf964f091",
    "0x9448E099761DA0253ef2fA9296D2ba77d322e28C",
]
exclude = [e.lower() for e in exclude]

# %%
set(
    e.lower()
    for e in [
        "0x78bc5ee9f11d133a08b331c2e18fe81be0ed02dc",
        "0x11a0c9270d88c99e221360bca50c2f6fda44a980",
        "0x9448e099761da0253ef2fa9296d2ba77d322e28c",
        "0x91b4c8de02c3396860d032eb987a51cb0dec56f6",
        "0xc7029e939075f48fa2d5953381660c7d01570171",
        "0x1b462629d6608354bc1a7f67f3d4a58105ab2534",
        "0x9d017bbb1e9ad1dc677307735b7c6b404e1c5c1b",
        "0x73a348ef3bbd14bdb98be1f92891582251ac4f45",
        "0x6ED562a792214AC325F2682302bD690237c6c08E",
        "0x8e9d9d3f7681dc49059d23254ec95395dd7e305d",
        "0x5ba7edc664b3c0955c317ecc8e24dd2f9f2a862e",
        "0xc6fd3b1dc606014cff8fc1e5a0c10d716dce12f3",
        "0xa50dccc889f41998d3343d0b73493b64c22a6ddc",
        "0x7ad7242A99F21aa543F9650A56D141C57e4F6081",
        "0x7ad7242A99F21aa543F9650A56D141C57e4F6081",
        "0x94cea04c51e7d3ec0a4a97ac0c3b3c9254c2ad41",
        "0x94cea04c51e7d3ec0a4a97ac0c3b3c9254c2ad41",
        "0x02944e3fb72aa13095d7cebd8389fc74bec8e48e",
        "0x097d72e1D9bbb8d0263477f9b20bEBF66f243AF4",
    ]
)

# %%
# len(_)

# %%
lists_sources = {str(name).split("/")[-1]: json.load(open(name, "r")) for name in files}

# %%
lists_sources["furo_0x4ab2FC6e258a0cA7175D05fF10C5cF798A672cAE.json"]

# %%
v = lists_sources["furo_0x4ab2FC6e258a0cA7175D05fF10C5cF798A672cAE.json"]
clean = {}
for index, r in v["balances"].items():
    addr = v["owners"][index]
    clean[addr] = sum(r) + clean.get(addr, 0)
lists_sources["furo_0x4ab2FC6e258a0cA7175D05fF10C5cF798A672cAE.json"] = clean
v = lists_sources["furo_0x4ab2FC6e258a0cA7175D05fF10C5cF798A672cAE.json"]

# %%
for key, vals in lists_sources.items():
    vals = {a.lower(): v for a, v in vals.items()}
    lists_sources[key] = vals

# %%
df = pd.DataFrame(lists_sources)
df.index = [i.lower() for i in df.index]
ignore = [i.lower() for i in ignore]

# %%
df = df.fillna(0)

# %%
for col in df.columns:
    # print(col)
    df[col] = df[col].astype(pd.Int64Dtype())

# %%
jade_column = [c for c in df.columns if "jade" in c][0]

# %%
for c in df.columns:
    split = c.split("_")
    addr = split[-1][:-5]
    kind = split[0]
    if kind != "airdrop":
        continue
    s = df[c].sum()
    df.loc[addr, jade_column] -= s
    # print(s)

# %%
333924349620 + 1898050578534 + 220382037499 + 73225174067 + 2184860508768


# %%
df["excluded"] = [i in ignore for i in df.index]

# %%
df3 = df[df.excluded == True]

# %%
df2 = df[df.excluded == False]

# %%
df3

# %%
(df.loc[:, jade_column].sum() - 671902820314501) // 1e9

# %%
jade_column

# %%
df3.loc["0x7ad7242a99f21aa543f9650a56d141c57e4f6081"]

# %%
target = 671902

# %%
check = (
    df3.loc["0x7ad7242a99f21aa543f9650a56d141c57e4f6081", jade_column]
    + df3.iloc[:, :].sum().sum()
    - df3.loc[:, jade_column].sum().sum()
    + df2.sum().sum()
)
(check) // 10 ** 9, target

# %%
df.to_csv("./data/BSC_FINAL_RAW.csv")
print("-- Wrote BSC_FINAL_RAW.csv --")

# %%
df2 = df[df.excluded == False]
df2["excluded2"] = [i in exclude + AIRDROPS for i in df2.index.values]

# %%

df_final = df2[df2["excluded2"] == False]
df_final.to_csv("./data/BSC_FINAL.csv")
print("-- Wrote BSC_FINAL.csv --")

# %%
df_final

# %%
df_finale1 = pd.read_csv("./data/BSC_FINAL.csv")
df_finale2 = pd.read_csv("./data/AVAX_FINAL.csv")

# %%
df_finale1.columns

# %%
df_finale1.sum()

# %%
df_finale1.rename(columns={"Unnamed: 0": "address"}, inplace=True)
df_finale2.rename(columns={"Unnamed: 0": "address"}, inplace=True)

# %%
for c in df_finale1:
    if "exclu" in c:
        df_finale1.drop(c, axis=1, inplace=True)
for c in df_finale2:
    if "exclu" in c:
        df_finale2.drop(c, axis=1, inplace=True)

# %%
len(set(df_finale1.address).union(set(df_finale2.address)))

# %%
DF = (
    df_finale1.join(
        df_finale2.set_index("address"),
        lsuffix="_bsc",
        rsuffix="_avax",
        on="address",
        how="outer",
    )
    .fillna(0)
    .reset_index(drop=True)
)
DF.set_index("address")

# %%
DF.astype(bool).sum(axis=1).max()

# %%
for col in DF.columns[1:]:
    # print(col)
    DF[col] = DF[col].astype(pd.Int64Dtype())

# %%
for col in DF.columns[1:]:
    # print(col)
    DF[col] = DF[col].astype(str)

# %%
DF.to_dict()

# %%
raw_data = DF.transpose().to_dict()

# %%
convert = [
    "jade_0x7ad7242A99F21aa543F9650A56D141C57e4F6081.json",
    "bond_0xD6C73ef5e71A350f8AE642C01Aad3d7637a0c1C8.json",
    "airdrop_0xb8e3729c9d337782703105e164254e5b9acb780b.json",
    "bond_0xb855ee49de8f05a441104c4e053a3be7ff45ae56.json",
    "airdrop_0x84bccd98ae46b14cb6ce645b43a5ef970160a114.json",
    "airdrop_0x0c41afa1b92b5c5ae50ef51d9c14e587a69304bc.json",
    "airdrop_0xa9abfb5e0f79e3f20e7305d8d1fe8faa9cc70e56.json",
    "bond_0x266a93EA88C002ff223E81E40300056289938142.json",
    "staking_0x097d72e1D9bbb8d0263477f9b20bEBF66f243AF4.json",
    "airdrop_0x124374a7ffb5195fc6d9ceedce5007658641a393.json",
    "furo_0x4ab2FC6e258a0cA7175D05fF10C5cF798A672cAE.json",
    "lp_0x46503d91D7a41FCbDC250E84ceE9D457d082D7b4.json",
    "bond_0xDcbB8a0FE62aE5064Bd36379eEe594Cc9861A384.json",
    "sablier_0x73f503fad13203c87889c3d5c567550b2d41d7a4.json",
    "airdrop_0xef874e86acca337ec2e744babd40d2b17ce5898e.json",
    "bond_0xf41E19fE47D63C7F6ec20722aF749D1aC625815D.json",
    "holders_0x80B010450fDAf6a3f8dF033Ee296E92751D603B3.json",
    "staking_0x273673f62198744c31129f6353f5bbd5b1d01ec0.json",
    "bond_0xab47ded800cee16950ab70f6063d0fe199a4c488.json",
    "lp_0x8DEF3929FDa2332b523488c0b4dDDeEa7553dB6f.json",
]
for idx, c in enumerate(convert):
    name = c.split("_")[0]
    addr = c.split("_")[1][:42]
    if name == "holders":
        name = "jade"
    if idx < 12:
        name += " on BSC"
    else:
        name += " on AVAX"
    convert[idx] = [c, {"name": name, "address": addr}]
convert = dict(convert)

# %%
DF

# %%
sums = DF.iloc[:, 1:].astype(int).sum(axis=1)

# %%
claim_data = dict(zip(DF.iloc[:, 0].values, sums))

# %%
from tqdm import tqdm

# %%
final_data = {}
for row in tqdm(raw_data.values()):
    address = row["address"]
    address_data = []
    i = 0
    for idx, item in row.items():
        if idx == "address":
            continue
        base = convert[idx].copy()
        base["amount"] = item
        if int(item) == 0:
            continue
        i += 1
        # if i > 5:
        #     print(address)

        address_data.append(base)
    if len(address_data):
        final_data[address] = address_data

# %%
set([len(r) for r in final_data.values()])

# %%
DF.iloc[:, 1:].sum(axis=1)

# %%
DF.to_csv("./FINAL_RAW.csv")
print("-- Wrote FINAL_RAW.csv --")

# %%
import json

json.dump(final_data, open("./final_data.json", "w"))

# %%
DF.shape

# %%
DF

# %%
DF.columns

# %%
DF.iloc[:, 1:].astype(int).sum()

# %%
groups = {
    "Total Jade (AVAX)": ["holders_0x80B010450fDAf6a3f8dF033Ee296E92751D603B3.json"],
    "Total sJade (AVAX)": ["staking_0x273673f62198744c31129f6353f5bbd5b1d01ec0.json"],
    "Total Jade (BSC)": ["jade_0x7ad7242A99F21aa543F9650A56D141C57e4F6081.json"],
    "Total sJade (BSC)": ["staking_0x097d72e1D9bbb8d0263477f9b20bEBF66f243AF4.json"],
    "Total Disc 1 Bonds v1": ["bond_0xDcbB8a0FE62aE5064Bd36379eEe594Cc9861A384.json"],
    "Total Disc 1 Bonds v2": ["bond_0xab47ded800cee16950ab70f6063d0fe199a4c488.json"],
    "Total Disc 2 Bonds": ["bond_0xf41E19fE47D63C7F6ec20722aF749D1aC625815D.json"],
    "Total Furo Streams": [
        "sablier_0x73f503fad13203c87889c3d5c567550b2d41d7a4.json",
        "furo_0x4ab2FC6e258a0cA7175D05fF10C5cF798A672cAE.json",
    ],
    "Old Olympus Bonds": [
        "bond_0x266a93EA88C002ff223E81E40300056289938142.json",
        "bond_0xD6C73ef5e71A350f8AE642C01Aad3d7637a0c1C8.json",
        "bond_0xb855ee49de8f05a441104c4e053a3be7ff45ae56.json",
    ],
    "Old Airdrop Contracts": [
        "airdrop_0xa9abfb5e0f79e3f20e7305d8d1fe8faa9cc70e56.json",
        "airdrop_0x84bccd98ae46b14cb6ce645b43a5ef970160a114.json",
        "airdrop_0x124374a7ffb5195fc6d9ceedce5007658641a393.json",
        "airdrop_0x0c41afa1b92b5c5ae50ef51d9c14e587a69304bc.json",
    ],
    "sJade Airdrop (AVAX)": ["airdrop_0xef874e86acca337ec2e744babd40d2b17ce5898e.json"],
    "LP on BSC": ["lp_0x46503d91D7a41FCbDC250E84ceE9D457d082D7b4.json"],
    "LP on AVAX": ["lp_0x8DEF3929FDa2332b523488c0b4dDDeEa7553dB6f.json"],
}

# %%
for group, cols in groups.items():
    print(group, DF.loc[:, cols].astype(int).sum().sum() / 1e9)
