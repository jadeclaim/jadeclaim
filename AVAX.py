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
bsc_balances_path = Path("./data/avax/balances")
files = [p for p in bsc_balances_path.iterdir()]

# %%
MULTICALL = "0x6e219eb5856388a28Fa8BD2311dedF8B4194422D"
ignore = [
    "0xf41E19fE47D63C7F6ec20722aF749D1aC625815D",
    "0xab47ded800cee16950ab70f6063d0fe199a4c488",
    "0xDcbB8a0FE62aE5064Bd36379eEe594Cc9861A384",
    "0x80B010450fDAf6a3f8dF033Ee296E92751D603B3",
    "0x8DEF3929FDa2332b523488c0b4dDDeEa7553dB6f",
    "0x73f503fad13203c87889c3d5c567550b2d41d7a4",
    "0x273673f62198744c31129f6353f5bbd5b1d01ec0",
    "0x3D9eAB723df76808bB84c05b20De27A2e69EF293",
    
]
jade = "0x80B010450fDAf6a3f8dF033Ee296E92751D603B3"
sJade = "0x3D9eAB723df76808bB84c05b20De27A2e69EF293"

# %%
exclude = [
    "0x000000000000000000000000000000000000dead",
    "0x9448e099761da0253ef2fa9296d2ba77d322e28c",
    "0x91b4c8de02c3396860d032eb987a51cb0dec56f6",
    "0x45ecfd1f5cf000a8320d8b88d53373bdf964f091",
    "0x273673f62198744c31129f6353f5bbd5b1d01ec0",
    "0x02944e3fb72aa13095d7cebd8389fc74bec8e48e",
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
AIRDROPS = ["0xef874e86acca337ec2e744babd40d2b17ce5898e"]

# %%
lists_sources = {str(name).split("/")[-1]: json.load(open(name, "r")) for name in files}

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
df = df // 10**9

# %%
jade_column = [c for c in df.columns if "holder" in c][0]

# %%
[c for c in df.columns if "holder" in c]

# %%
for col in df.columns:
    # print(col)
    df[col] = df[col].astype(pd.Int64Dtype())

# %%

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
df["excluded"] = [i in ignore for i in df.index]

# %%
df.to_csv("./data/AVAX_FINAL_RAW.csv")
print("-- Wrote AVAX_FINAL_RAW.csv --")

# %%
df2 = df[df.excluded == False]
df2["excluded2"] = [i in exclude+AIRDROPS for i in df2.index.values]
df_final = df2[df2["excluded2"] == False]
df_final.to_csv("./data/AVAX_FINAL.csv")
print("-- Wrote AVAX_FINAL.csv --")

# %%
df3 = df[df.excluded == True]

# %%
target = 627304

# %%
check = (
    df3.loc[jade.lower()]["holders_0x80B010450fDAf6a3f8dF033Ee296E92751D603B3.json"]
    + df3.sum().sum()
    - df3["holders_0x80B010450fDAf6a3f8dF033Ee296E92751D603B3.json"].sum()
    + df2.sum().sum()
)
check // 1e9, target

# %%
