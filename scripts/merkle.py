import random
from abc import ABC, abstractmethod
from typing import Callable, Optional, Union

from brownie import web3
from tqdm import tqdm

# possible solutions to replace DF = ...
# DF = pd.read_csv(DATA_PATH)
# DF = pd.read_csv(DATA_PATH, header=0)
# Or any combination of the following
# The Amounts unit will be 10**6 for 1 usdc. Make sure that all the data is in plain integer form
# no scientific form, no decimal places
# The original data is in 10**9, since before convertion they are jade (BSC)


class Leaf(ABC):
    index: int

    @property
    @abstractmethod
    def hex_value(self) -> str:
        pass


class LeafData(Leaf):
    account: str
    amount: int

    def __init__(self, index, account, amount):
        self.index = index
        self.account = account.replace("0x", "").zfill(40)
        self.amount = amount

    @property
    def hex_value(self):
        amount = self.amount
        if isinstance(amount, str) and not amount.startswith("0x"):
            amount = int(amount)
        if isinstance(amount, int):
            amount = hex(amount).replace("0x", "").zfill(64)
        else:
            amount = amount.replace("0x", "").zfill(64)
        account = self.account.replace("0x", "").zfill(64)
        return f"{account}{amount}"

    def __str__(self):
        return f"{self.index} : {self.account} {self.amount}"

    def __repr__(self):
        return f"{self.index} : {self.account} {self.amount}"

    def pure_leaf(self):
        amount = self.amount
        if isinstance(amount, str) and not amount.startswith("0x"):
            amount = int(amount)
        if isinstance(amount, int):
            amount = hex(amount).replace("0x", "").zfill(64)
        else:
            amount = amount.replace("0x", "").zfill(64)
        return f"{self.account}{amount}"


def pad_hex(hex_str, length=64):
    return hex_str.replace("0x", "").zfill(length)


def concat_hex(*args):
    return "".join([pad_hex(arg) for arg in args])


def keccak(x):
    # print(x)
    x = x.replace("0x", "")
    return web3.sha3(hexstr=x).hex()


class MerkleTree:
    data: list[Leaf]
    hash_func: Optional[Callable[[str], str]]
    parent: Optional["MerkleTree"]
    leaf: Optional[Leaf]
    left: Optional["MerkleTree"]
    right: Optional["MerkleTree"]
    hash: Optional[str]
    index: Optional[int]
    cutoff: Optional[int]
    size: int

    def __init__(self, data, hash_func: Callable[[str], str] = keccak, parent=None):
        self.data = data
        self.data.sort(key=lambda x: x.index)
        self.hash_func = hash_func
        self.parent = parent
        self.leaf = None
        self.left = None
        self.right = None
        self.hash = None
        self.index = None
        self.cutoff = None
        self._build()

    def _build(self):
        self.size = len(self.data)
        if len(self.data) == 1:
            self.leaf = self.data[0]
            self.hash = self.hash_func(self.leaf.hex_value)
            self.hash = self.hash_func(self.hash)
            return

        left_data = self.data[: len(self.data) // 2]
        right_data = self.data[len(self.data) // 2 :]
        self.cutoff = max([leaf.index for leaf in left_data])

        if len(left_data) > 0:
            self.left = MerkleTree(left_data, self.hash_func, self)
        if len(right_data) > 0:
            self.right = MerkleTree(right_data, self.hash_func, self)

        # print(self.left.hash, self.right.hash)

        # print(type(self.left.hash), type(self.right.hash))
        if self.left is None:
            self.hash = self.right.hash
        elif self.right is None:
            self.hash = self.left.hash
        elif int(self.left.hash, 16) <= int(self.right.hash, 16):
            self.hash = self.hash_func(self.left.hash + self.right.hash)
        elif int(self.left.hash, 16) > int(self.right.hash, 16):
            self.hash = self.hash_func(self.right.hash + self.left.hash)

    @property
    def is_root(self):
        return self.parent is None

    def get_proof(self, node_index):
        if node_index >= self.size and self.is_root:
            raise ValueError("Node index out of range")
        if self.leaf is not None:
            assert self.leaf.index == node_index
            return []

        if node_index <= self.cutoff:
            if self.right is not None:
                proof = [self.right.hash] + self.left.get_proof(node_index)
            else:
                proof = self.left.get_proof(node_index)
        else:
            if self.left is not None:
                proof = [self.left.hash] + self.right.get_proof(node_index)
            else:
                proof = self.right.get_proof(node_index)
        if self.is_root:
            return list(reversed(proof))
        return proof

    def dump(self):
        if self.leaf is not None:
            return (self.leaf.amount, self.leaf.account, self.leaf.index)
        return {"left": self.left.dump(), "right": self.right.dump()}

    def test_proof(self, node_value, proof):
        node_value = self.hash_func(self.hash_func(node_value))
        for element in proof:
            if int(element, 16) > int(node_value, 16):
                node_value = self.hash_func(node_value + element)
            else:
                node_value = self.hash_func(element + node_value)
            # print(node_value)
        return node_value == self.hash

    def print(self):
        raise "Not implemented"
        down_char = "└─"
        split_char = "├─"
        pass_char = "│ "
        indent_level = 0


class Empty:
    pass


class StandardMerkleTree:
    nodes = []
    leaves: list[LeafData] = []
    hash_func: Optional[Callable[[str], str]]
    data: list[Union[Empty, LeafData]]

    def __init__(self, leaves, hash_func=keccak):
        self.leaves = leaves
        hashed_leaves = [hash_func(hash_func(leaf.hex_value)) for leaf in leaves]
        leaves_zip = zip(hashed_leaves, leaves)
        leaves_zip = sorted(leaves_zip, reverse=True)
        self.leaves = [leaf[1] for leaf in leaves_zip]
        self.hashed_leaves = [leaf[0] for leaf in leaves_zip]
        self.hash_func = hash_func
        self.N = len(bin(len(leaves))) - 2
        self.leaves_num = len(leaves)
        self.data = [Empty] * (self.leaves_num - 1) + self.hashed_leaves
        self.build()

    def build(self):
        max_index = len(self.data)
        print(max_index)
        for step in range(len(self.data)):
            i = max_index - 1 - step
            # print("ok")
            node = self.data[i]
            if node is not Empty:
                continue
            bigger_child_index = 2 * (i + 1)
            smaller_child_index = bigger_child_index - 1
            if smaller_child_index >= max_index:
                print("Issue at index ", i)
                continue
            if smaller_child_index == max_index:
                self.data[i] = self.data[smaller_child_index]
                continue
            hashA = self.data[smaller_child_index]
            hashB = self.data[bigger_child_index]
            if int(hashA, 16) <= int(hashB, 16):
                hash = self.hash_func(hashA + hashB)
            if int(hashA, 16) > int(hashB, 16):
                hash = self.hash_func(hashB + hashA)
            self.data[i] = hash

    @property
    def root(self):
        return self.data[0]

    @property
    def hash(self):
        return self.data[0]

    def get_proof(self, index):
        max_index = len(self.data)
        index_in_data = self.leaves_num - 1 + index
        assert index_in_data < max_index
        proof = []
        while index_in_data > 0:
            brother = index_in_data - (-1) ** (index_in_data % 2)
            proof.append(self.data[brother])
            index_in_data = (index_in_data - 1) // 2
        return proof

    def get_leaf_index_by_leaf(self, leaf):
        return self.leaves.index(leaf)

    def get_leaf_index_by_address(self, address):
        address = address.replace("0x", "")
        return self.get_leaf_index_by_leaf(
            list(filter(lambda x: x.account.lower() == address.lower(), self.leaves))[0]
        )

    def get_in_data_index(self, index):
        return self.leaves_num - 1 + index

    def test_proof(self, node_value, proof):
        print(node_value)
        node_value = self.hash_func(self.hash_func(node_value))
        for element in proof:
            print(element + node_value)
            if int(element, 16) > int(node_value, 16):
                node_value = self.hash_func(node_value + element)
            else:
                node_value = self.hash_func(element + node_value)
            # print(node_value)
        return node_value == self.hash

    def to_json(self):
        data = {}
        for index in tqdm(range(len(self.leaves))):
            leaf = self.leaves[index]
            proof = self.get_proof(index)
            data["0x" + pad_hex(leaf.account, 40)] = {
                "amount": str(leaf.amount),
                "proof": proof,
            }
        return data


def get_random_address():
    characters = [str(i) for i in list(range(0, 10)) + ["A", "B", "C", "D", "E", "F"]]
    return web3.toChecksumAddress(
        "0x" + "".join([random.choice(characters) for _ in range(0, 40)])
    )
