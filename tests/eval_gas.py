from brownie import Airdrop, MintableERC20, Wei, accounts, chain


def test():
    owner = accounts[0]
    params = {"from": owner}

    token = MintableERC20.deploy("", "", 18, params)
    token.toggleSupplyManager(owner, params)
    contract = Airdrop.deploy(token, params)
    token.mint(contract, Wei("10000 ethers"), params)
    users = ["0x" + hex(i + 1).replace("0x", "").zfill(40) for i in range(200)]
    amounts = [10**18 for _ in users]
    contract.setAmounts(users, amounts, params)
