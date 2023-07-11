import pytest
from brownie import (ZERO_ADDRESS, FWDToken, MintableERC20, Redeem,
                     TokenStaking, Wei, accounts, chain, interface, network,
                     sFWDToken)

from ..utils import *


@pytest.fixture(scope="module")
def deployer():
    return accounts[-1]


@pytest.fixture(scope="module", autouse=True)
def usdc(deployer):
    token = MintableERC20.deploy("usdc", "usdc", 6, {"from": deployer})
    return token


@pytest.fixture(scope="module", autouse=True)
def fwd(deployer):
    token = FWDToken.deploy({"from": deployer})
    return token


@pytest.fixture(scope="module", autouse=True)
def sfwd(deployer):
    token = sFWDToken.deploy({"from": deployer})
    return token


@pytest.fixture(scope="module", autouse=True)
def deployer_params(deployer):
    return {"from": deployer}


@pytest.fixture(scope="module", autouse=True)
def redeem_contract(deployer_params, usdc, fwd):
    redeem, proxy_admin = deploy_upgradeable_contract(
        deployer_params,
        Redeem,
        "__Redeem_init",
        None,
        fwd,
        usdc,
        2093,
    )
    return redeem


@pytest.fixture(scope="module", autouse=True)
def staking_contract(deployer_params, usdc, fwd, sfwd):
    staking, proxy_admin = deploy_upgradeable_contract(
        deployer_params, TokenStaking, "__TokenStaking_init", None, fwd, sfwd
    )
    sfwd.transferOwnership(staking, deployer_params)
    return staking


@pytest.fixture(scope="module", autouse=True)
def mint_tokens(deployer_params, usdc, redeem_contract):
    usdc.mint(redeem_contract, Wei("200 ether") / 10**12, deployer_params)
    # jade.mint(deployer_params["from"], Wei("100 ether"), deployer_params)
    # jade.mint(client, Wei("100 ether"), deployer_params)


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass
