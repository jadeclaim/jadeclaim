import json

import pandas as pd
from merkle import *

DATA_PATH = "./FINAL.csv"
OUTPUT_PATH = "./tree.json"
price = 2.6

DF = pd.read_csv(DATA_PATH, index_col=0)
print(f"COLUMNS ARE: {DF.columns}", "Please check that no weird name are here")
print(f"DATA length is {DF.shape}", "Please check the coherency of the data you put in")
sums = DF.iloc[:, 1:].astype(int).sum(axis=1)
claim_data = dict(zip(DF.iloc[:, 0].values, sums))
claim_data = {key: int(v * price / 10**3) for key, v in claim_data.items() if v > 0}
assert [
    isinstance(val, int) for val in claim_data.values()
], "Some of the data is not in a correct form"

LEAVES = [
    LeafData(i, account, amount)
    for i, (account, amount) in enumerate(claim_data.items())
]


MERKLE_TREE = StandardMerkleTree(LEAVES)
# gab_index = MERKLE_TREE.get_leaf_index_by_address(
#     "0x361041A2609c9deFE2A0DC99ed3E1bC0220D92Ac"
# )
# print(MERKLE_TREE.leaves[gab_index])
# gab = MERKLE_TREE.get_proof(gab_index)
#
# print(gab)

print(
    f"The root is {MERKLE_TREE.root}. You will need to create an aidrop with this to work"
)
json.dump(MERKLE_TREE.to_json(), open(OUTPUT_PATH, "w"))
