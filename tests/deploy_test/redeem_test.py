import pytest
from brownie import (MintableERC20, Wei, accounts, chain, interface, network,
                     reverts)
from py_vector.common.testing import debug_decorator
from pytest import approx

from ..utils import *


def test_deploy():
    pass


def test_redeem(
    redeem_contract,
    deployer_params,
    fwd,
    usdc,
):
    redeem = redeem_contract
    amount = Wei("1 ether")
    client_params = deployer_params
    client = client_params["from"]
    prev_total_supply = fwd.totalSupply()
    fwd.approve(redeem, 2 * amount, client_params)
    initial_balance = fwd.balanceOf(client)
    redeem.redeemToken(amount, 0, client_params)
    assert initial_balance - fwd.balanceOf(client) == amount
    assert fwd.balanceOf(redeem) == 0
    assert (
        usdc.balanceOf(client)
        == amount * redeem.tokenPriceInUsd() // 10**2 // 10**12
    )
    assert fwd.totalSupply() == prev_total_supply - amount


def test_price_go_up(redeem_contract, deployer_params, fwd, usdc):
    redeem = redeem_contract
    redeem.setTokenPrice(3000, 2, deployer_params)
    redeem.setTokenPrice(31000, 3, deployer_params)
    with reverts("Price can no longer go down"):
        redeem.setTokenPrice(3000, 2, deployer_params)


def test_modify_price(redeem_contract, deployer_params, fwd, usdc):
    redeem = redeem_contract
    amount = Wei("1 ether")
    client_params = deployer_params
    client = client_params["from"]
    fwd.approve(redeem, 2 * amount, client_params)
    initial_balance = fwd.balanceOf(client)
    redeem.redeemToken(amount, 0, client_params)
    assert initial_balance - fwd.balanceOf(client) == amount
    assert (
        usdc.balanceOf(client)
        == amount * redeem.tokenPriceInUsd() // 10**2 // 10**12
    )
    chain.undo()
    redeem.setTokenPrice(3000, 2, deployer_params)
    initial_balance = fwd.balanceOf(client)
    redeem.redeemToken(amount, 0, client_params)
    assert initial_balance - fwd.balanceOf(client) == amount
    assert (
        usdc.balanceOf(client)
        == amount * redeem.tokenPriceInUsd() // 10**2 // 10**12
    )


def test_get_back_tokens(redeem_contract, deployer_params, fwd, usdc):
    redeem = redeem_contract
    amount = Wei("1 ether")
    client_params = deployer_params
    deployer = deployer_params["from"]
    b2 = usdc.balanceOf(redeem)
    assert b2
    with reverts():
        redeem.scoopTokens(usdc, usdc.balanceOf(redeem), {"from": accounts[1]})
    redeem.scoopTokens(usdc, usdc.balanceOf(redeem), deployer_params)
    redeem.scoopTokens(usdc, usdc.balanceOf(redeem), deployer_params)
    assert usdc.balanceOf(redeem) == 0
    assert usdc.balanceOf(deployer) == b2


def test_transfer_ownership(redeem_contract, deployer, deployer_params, fwd, usdc):
    client = accounts[1]
    redeem = redeem_contract
    redeem.transferOwnership(client, deployer_params)
    b2 = usdc.balanceOf(redeem)
    assert b2
    redeem.scoopTokens(usdc, usdc.balanceOf(redeem), {"from": client})
    assert usdc.balanceOf(client) == b2
