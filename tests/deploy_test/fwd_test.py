from brownie import (MintableERC20, Wei, accounts, chain, interface, network,
                     reverts)
from py_vector.common.testing import debug_decorator
from pytest import approx

from ..utils import *


def test_deploy():
    pass


def test_snapshot(
    deployer_params,
    deployer,
    fwd,
):
    b0 = fwd.balanceOf(deployer)
    with reverts("Only allowed sender can snapshot"):
        snapshot_id = fwd.snapshot(deployer_params)
    fwd.setSnapshotAuthorization(deployer, True, deployer_params)
    snapshot_id = fwd.snapshot(deployer_params)
    snapshot_id = snapshot_id.return_value
    fwd.transfer(accounts[2], b0 // 2, deployer_params)

    assert fwd.balanceOf(deployer) == b0 - b0 // 2
    assert fwd.balanceOf(accounts[2]) == b0 // 2
    assert fwd.balanceOfAt(deployer, snapshot_id) == b0
    assert fwd.balanceOfAt(accounts[2], snapshot_id) == 0

    second_id = fwd.snapshot(deployer_params)
    second_id = second_id.return_value
    fwd.burn(fwd.balanceOf(deployer), deployer_params)
    assert fwd.totalSupply() == b0 // 2
    assert fwd.totalSupplyAt(second_id) == b0
