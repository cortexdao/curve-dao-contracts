import itertools

import brownie
import pytest


def test_set_rate_permission(accounts, cortex_minter):
    with brownie.reverts("dev: admin only"):
        cortex_minter.set_rate(1e18, {"from": accounts[1]})


def test_set_rate(accounts, cortex_minter):
    rate = 23432987928798798897897
    cortex_minter.set_rate(rate, {"from": accounts[0]})
    assert cortex_minter.rate() == rate


def test_add_gauge_permission(accounts, cortex_minter):
    with brownie.reverts("dev: admin only"):
        cortex_minter.add_gauge(accounts[0], {"from": accounts[1]})


def test_remove_gauge_permission(accounts, cortex_minter):
    with brownie.reverts("dev: admin only"):
        cortex_minter.remove_gauge(accounts[0], {"from": accounts[1]})


def test_gauge_registration(accounts, cortex_minter):
    cortex_minter.add_gauge(accounts[1], {"from": accounts[0]})
    assert cortex_minter.gauge_registered(accounts[1])

    cortex_minter.remove_gauge(accounts[1], {"from": accounts[0]})
    assert not cortex_minter.gauge_registered(accounts[1])

