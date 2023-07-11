import json

import pandas as pd
from brownie import Contract, Wei, accounts, chain, network


equivalent_names = {'ava-main': ['avax-main'], "AWS": ['aws-fork1']}


import json

import eth_utils
from brownie import Contract, ProxyAdmin, TransparentUpgradeableProxy, Wei, network


equivalent_names = {'ava-main': ['avax-main'], "AWS": ['aws-fork1']}


def encode_function_data(initializer=None, *args):
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    else:
        return initializer.encode_input(*args)


def deploy_upgradeable_contract(user_params, implementation_container, arg_name, proxy_admin=None, *args):
    container_name = implementation_container._name

    implementation = implementation_container.deploy(
        user_params,
    )
    implementation_encoded_initializer_function = encode_function_data(
        getattr(implementation, arg_name),
        *args
    )

    if not proxy_admin:
        proxy_admin = ProxyAdmin.deploy(
            user_params,
        )
    contract = TransparentUpgradeableProxy.deploy(
        implementation.address,
        proxy_admin.address,
        implementation_encoded_initializer_function,
        user_params
    )
    contract = Contract.from_abi(container_name, contract.address, implementation_container.abi)
    return contract, proxy_admin


def upgrade(
    account,
    proxy,
    newimplementation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args
):
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                newimplementation_address,
                encoded_function_call,
                {"from": account},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, newimplementation_address, {"from": account}
            )
    else:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeToAndCall(
                newimplementation_address, encoded_function_call, {"from": account}
            )
        else:
            transaction = proxy.upgradeTo(newimplementation_address, {"from": account})
    return transaction


def upgrade_in_test(
    account,
    proxy,
    newimplementation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args
):
    transaction = None
    if proxy_admin_contract:
        proxy_admin_contract.submitUpgrade(proxy, newimplementation_address, {"from": account})
        chain.sleep(4 * 24 * 3600 + 1)
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                encoded_function_call,
                {"from": account},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, {"from": account}
            )
    else:
        proxy.submitUpgrade(newimplementation_address, {"from": account})
        chain.sleep(4 * 24 * 3600 + 1)
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeToAndCall(
                encoded_function_call, {"from": account}
            )
        else:
            transaction = proxy.upgradeTo({"from": account})
    return transaction


class AddressCache:
    cid = None
    j = {}

    def __init__(self, chain_id):
        for equivalent_name, equivalences in equivalent_names.items():
            if chain_id in equivalences:
                chain_id = equivalent_name
                break
        self.cid = chain_id
        self.j = json.load(open('./addresses_cache.json', 'r'))

    def load_address(self, key):
        return self.j.get(self.cid, {}).get(key)

    def save_addresses(self, **kwargs):
        if self.cid not in self.j:
            self.j[self.cid] = {}

        for key, contract in kwargs.items():
            self.j[self.cid][key] = (contract if not hasattr(contract, 'address') else contract.address)
        json.dump(self.j, open('./addresses_cache.json', 'w'))


# def load_all_addresses():
#     cid = str(network.chain._chainid)
#     try:
#         j = json.load(open('./addresses_cache.json', 'r'))[cid]
#     except:
#         return {}
#     return j

# def load_address(key):
#     j = load_all_addresses()
#     return j.get(key, None)

# def save_addresses(**kwargs):
#     j =  load_all_addresses()
#     cid = str(network.chain._chainid)
#     if cid not in j:
#         j[cid] = {}

#     for key, contract in kwargs.items():
#         j[cid][key] = contract if type(contract) == str else contract.address
#     json.dump(j, open('./addresses_cache.json', 'w'))


def get_abi(contract):

    with open(f'./build/contracts/{contract}.json', 'r') as f:
        data = json.load(f)
    return data['abi']


def magic_loader(name, address):
    return Contract.from_abi(name, address, get_abi(name))


def get_tx_params(_user):
    return {"from": _user, "gas_price": Wei('60 gwei')}


def setup_csv_wallet(storage, deployer, tokens):
    df = pd.read_csv('./bonding_1.csv')
    deployer = accounts.load('jade', password='jade')
    df['final_jlp_balance'] = df['final_jlp_balance'].apply(lambda x: float(x.replace(',', '')))
    df = df[(df['final_jlp_balance'] > 0) | (df['Staking on Feb 1'] == 1)]
    df['final_jlp_balance'] *= 10**18
    clients = list(df['test-wallet_id'].values)
    tiers = list(df['diamond_tier'].fillna("0").values)
    tiers = [int(t.upper().replace("--", "0").replace('A', '').replace('B', '')) for t in tiers]
    balances = list(df['final_jlp_balance'].values)
    # for wallet in clients:
    #     for token in tokens:
    #         token.mint(wallet, 10000 * 10**token.decimals(), {"from": deployer})
    storage.registerMultipleUsers(clients, balances, tiers, {'from': deployer})
