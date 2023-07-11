import pytest
from brownie import (MintableERC20, Wei, accounts, chain, interface, network,
                     reverts)
from py_vector.common.testing import debug_decorator
from pytest import approx

from ..utils import *


def test_deploy():
    pass


def test_staking(
    staking_contract,
    deployer_params,
    deployer,
    fwd,
    sfwd,
):
    staking = staking_contract
    amount = Wei("1 ether")
    b = fwd.balanceOf(deployer)
    sb = sfwd.balanceOf(deployer)
    fwd.approve(staking, amount, deployer_params)
    staking.stake(amount, deployer, deployer_params)
    assert fwd.balanceOf(deployer) - b == -amount
    assert sfwd.balanceOf(deployer) - sb == amount
    assert fwd.balanceOf(staking) == amount
    assert sfwd.totalSupply() == amount

    sfwd.approve(staking, amount, deployer_params)
    staking.unstake(amount, deployer_params)

    assert fwd.balanceOf(deployer) == b
    assert sfwd.balanceOf(deployer) == sb
