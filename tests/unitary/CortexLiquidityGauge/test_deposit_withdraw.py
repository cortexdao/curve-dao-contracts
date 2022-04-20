import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def deposit_setup(accounts, cortex_gauge, mock_lp_token):
    mock_lp_token.approve(cortex_gauge, 2 ** 256 - 1, {"from": accounts[0]})


def test_deposit(accounts, cortex_gauge, mock_lp_token):
    balance = mock_lp_token.balanceOf(accounts[0])
    cortex_gauge.deposit(100000, {"from": accounts[0]})

    assert mock_lp_token.balanceOf(cortex_gauge) == 100000
    assert mock_lp_token.balanceOf(accounts[0]) == balance - 100000
    assert cortex_gauge.totalSupply() == 100000
    assert cortex_gauge.balanceOf(accounts[0]) == 100000


def test_deposit_zero(accounts, cortex_gauge, mock_lp_token):
    balance = mock_lp_token.balanceOf(accounts[0])
    cortex_gauge.deposit(0, {"from": accounts[0]})

    assert mock_lp_token.balanceOf(cortex_gauge) == 0
    assert mock_lp_token.balanceOf(accounts[0]) == balance
    assert cortex_gauge.totalSupply() == 0
    assert cortex_gauge.balanceOf(accounts[0]) == 0


def test_deposit_insufficient_balance(accounts, cortex_gauge, mock_lp_token):
    with brownie.reverts():
        cortex_gauge.deposit(100000, {"from": accounts[1]})


def test_withdraw(accounts, cortex_gauge, mock_lp_token):
    balance = mock_lp_token.balanceOf(accounts[0])

    cortex_gauge.deposit(100000, {"from": accounts[0]})
    cortex_gauge.withdraw(100000, {"from": accounts[0]})

    assert mock_lp_token.balanceOf(cortex_gauge) == 0
    assert mock_lp_token.balanceOf(accounts[0]) == balance
    assert cortex_gauge.totalSupply() == 0
    assert cortex_gauge.balanceOf(accounts[0]) == 0


def test_withdraw_zero(accounts, cortex_gauge, mock_lp_token):
    balance = mock_lp_token.balanceOf(accounts[0])
    cortex_gauge.deposit(100000, {"from": accounts[0]})
    cortex_gauge.withdraw(0, {"from": accounts[0]})

    assert mock_lp_token.balanceOf(cortex_gauge) == 100000
    assert mock_lp_token.balanceOf(accounts[0]) == balance - 100000
    assert cortex_gauge.totalSupply() == 100000
    assert cortex_gauge.balanceOf(accounts[0]) == 100000


def test_withdraw_new_epoch(accounts, chain, cortex_gauge, mock_lp_token):
    balance = mock_lp_token.balanceOf(accounts[0])

    cortex_gauge.deposit(100000, {"from": accounts[0]})
    chain.sleep(86400 * 400)
    cortex_gauge.withdraw(100000, {"from": accounts[0]})

    assert mock_lp_token.balanceOf(cortex_gauge) == 0
    assert mock_lp_token.balanceOf(accounts[0]) == balance
    assert cortex_gauge.totalSupply() == 0
    assert cortex_gauge.balanceOf(accounts[0]) == 0
