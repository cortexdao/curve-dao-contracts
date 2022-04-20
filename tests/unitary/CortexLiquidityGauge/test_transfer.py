#!/usr/bin/python3
import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(accounts, gauge_controller, minter, cortex_gauge, token, mock_lp_token):
    token.set_minter(minter, {"from": accounts[0]})

    gauge_controller.add_type(b"Liquidity", 10 ** 10, {"from": accounts[0]})
    gauge_controller.add_gauge(cortex_gauge, 0, 0, {"from": accounts[0]})

    mock_lp_token.approve(cortex_gauge, 2 ** 256 - 1, {"from": accounts[0]})
    cortex_gauge.deposit(10 ** 18, {"from": accounts[0]})


def test_sender_balance_decreases(accounts, cortex_gauge):
    sender_balance = cortex_gauge.balanceOf(accounts[0])
    amount = sender_balance // 4

    cortex_gauge.transfer(accounts[1], amount, {"from": accounts[0]})

    assert cortex_gauge.balanceOf(accounts[0]) == sender_balance - amount


def test_receiver_balance_increases(accounts, cortex_gauge):
    receiver_balance = cortex_gauge.balanceOf(accounts[1])
    amount = cortex_gauge.balanceOf(accounts[0]) // 4

    cortex_gauge.transfer(accounts[1], amount, {"from": accounts[0]})

    assert cortex_gauge.balanceOf(accounts[1]) == receiver_balance + amount


def test_total_supply_not_affected(accounts, cortex_gauge):
    total_supply = cortex_gauge.totalSupply()
    amount = cortex_gauge.balanceOf(accounts[0])

    cortex_gauge.transfer(accounts[1], amount, {"from": accounts[0]})

    assert cortex_gauge.totalSupply() == total_supply


def test_returns_true(accounts, cortex_gauge):
    amount = cortex_gauge.balanceOf(accounts[0])
    tx = cortex_gauge.transfer(accounts[1], amount, {"from": accounts[0]})

    assert tx.return_value is True


def test_transfer_full_balance(accounts, cortex_gauge):
    amount = cortex_gauge.balanceOf(accounts[0])
    receiver_balance = cortex_gauge.balanceOf(accounts[1])

    cortex_gauge.transfer(accounts[1], amount, {"from": accounts[0]})

    assert cortex_gauge.balanceOf(accounts[0]) == 0
    assert cortex_gauge.balanceOf(accounts[1]) == receiver_balance + amount


def test_transfer_zero_tokens(accounts, cortex_gauge):
    sender_balance = cortex_gauge.balanceOf(accounts[0])
    receiver_balance = cortex_gauge.balanceOf(accounts[1])

    cortex_gauge.transfer(accounts[1], 0, {"from": accounts[0]})

    assert cortex_gauge.balanceOf(accounts[0]) == sender_balance
    assert cortex_gauge.balanceOf(accounts[1]) == receiver_balance


def test_transfer_to_self(accounts, cortex_gauge):
    sender_balance = cortex_gauge.balanceOf(accounts[0])
    amount = sender_balance // 4

    cortex_gauge.transfer(accounts[0], amount, {"from": accounts[0]})

    assert cortex_gauge.balanceOf(accounts[0]) == sender_balance


def test_insufficient_balance(accounts, cortex_gauge):
    balance = cortex_gauge.balanceOf(accounts[0])

    with brownie.reverts():
        cortex_gauge.transfer(accounts[1], balance + 1, {"from": accounts[0]})


def test_transfer_event_fires(accounts, cortex_gauge):
    amount = cortex_gauge.balanceOf(accounts[0])
    tx = cortex_gauge.transfer(accounts[1], amount, {"from": accounts[0]})

    assert tx.events["Transfer"].values() == [accounts[0], accounts[1], amount]
