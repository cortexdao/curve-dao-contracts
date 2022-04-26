import itertools

import brownie
import pytest

MONTH = 86400 * 30
WEEK = 7 * 86400


@pytest.fixture(scope="module", autouse=True)
def minter_setup(accounts, mock_lp_token, token, cortex_minter, gauge_controller, three_cortex_gauges, chain):
    token.set_minter(cortex_minter, {"from": accounts[0]})

    # ensure the tests all begin at the start of the epoch week
    chain.mine(timestamp=(chain.time() / WEEK + 1) * WEEK)

    # add gauges
    for i in range(3):
        cortex_minter.add_gauge(three_cortex_gauges[i], {"from": accounts[0]})

    # transfer tokens
    for acct in accounts[1:4]:
        mock_lp_token.transfer(acct, 1e18, {"from": accounts[0]})

    # approve gauges
    for gauge, acct in itertools.product(three_cortex_gauges, accounts[1:4]):
        mock_lp_token.approve(gauge, 1e18, {"from": acct})

    # set the total emissions rate
    cortex_minter.set_rate(1e18, {"from": accounts[0]})


def test_mint(accounts, chain, three_cortex_gauges, cortex_minter, token):
    three_cortex_gauges[0].deposit(1e18, {"from": accounts[1]})

    chain.sleep(MONTH)
    cortex_minter.mint(three_cortex_gauges[0], {"from": accounts[1]})
    expected = three_cortex_gauges[0].integrate_fraction(accounts[1])

    assert expected > 0
    assert token.balanceOf(accounts[1]) == expected
    assert cortex_minter.minted(accounts[1], three_cortex_gauges[0]) == expected


def test_mint_immediate(accounts, chain, three_cortex_gauges, cortex_minter, token):
    three_cortex_gauges[0].deposit(1e18, {"from": accounts[1]})
    t0 = chain.time()
    chain.sleep((t0 + WEEK) // WEEK * WEEK - t0 + 1)  # 1 second more than enacting the weights

    cortex_minter.mint(three_cortex_gauges[0], {"from": accounts[1]})
    balance = token.balanceOf(accounts[1])

    assert balance > 0
    assert cortex_minter.minted(accounts[1], three_cortex_gauges[0]) == balance


def test_mint_multiple_same_gauge(accounts, chain, three_cortex_gauges, cortex_minter, token):
    three_cortex_gauges[0].deposit(1e18, {"from": accounts[1]})

    chain.sleep(MONTH)
    cortex_minter.mint(three_cortex_gauges[0], {"from": accounts[1]})
    balance = token.balanceOf(accounts[1])

    chain.sleep(MONTH)
    cortex_minter.mint(three_cortex_gauges[0], {"from": accounts[1]})
    expected = three_cortex_gauges[0].integrate_fraction(accounts[1])
    final_balance = token.balanceOf(accounts[1])

    assert final_balance > balance
    assert final_balance == expected
    assert cortex_minter.minted(accounts[1], three_cortex_gauges[0]) == expected


def test_mint_multiple_gauges(accounts, chain, three_cortex_gauges, cortex_minter, token):
    for i in range(3):
        three_cortex_gauges[i].deposit((i + 1) * 10 ** 17, {"from": accounts[1]})

    chain.sleep(MONTH)

    for i in range(3):
        cortex_minter.mint(three_cortex_gauges[i], {"from": accounts[1]})

    total_minted = 0
    for i in range(3):
        gauge = three_cortex_gauges[i]
        minted = cortex_minter.minted(accounts[1], gauge)
        assert minted == gauge.integrate_fraction(accounts[1])
        total_minted += minted

    assert token.balanceOf(accounts[1]) == total_minted


def test_mint_after_withdraw(accounts, chain, three_cortex_gauges, cortex_minter, token):
    three_cortex_gauges[0].deposit(1e18, {"from": accounts[1]})

    chain.sleep(2 * WEEK)
    three_cortex_gauges[0].withdraw(1e18, {"from": accounts[1]})
    cortex_minter.mint(three_cortex_gauges[0], {"from": accounts[1]})

    assert token.balanceOf(accounts[1]) > 0


def test_mint_multiple_after_withdraw(accounts, chain, three_cortex_gauges, cortex_minter, token):
    three_cortex_gauges[0].deposit(1e18, {"from": accounts[1]})

    chain.sleep(10)
    three_cortex_gauges[0].withdraw(1e18, {"from": accounts[1]})
    cortex_minter.mint(three_cortex_gauges[0], {"from": accounts[1]})
    balance = token.balanceOf(accounts[1])

    chain.sleep(10)
    cortex_minter.mint(three_cortex_gauges[0], {"from": accounts[1]})

    assert token.balanceOf(accounts[1]) == balance


def test_no_deposit(accounts, chain, three_cortex_gauges, cortex_minter, token):
    cortex_minter.mint(three_cortex_gauges[0], {"from": accounts[1]})

    assert token.balanceOf(accounts[1]) == 0
    assert cortex_minter.minted(accounts[1], three_cortex_gauges[0]) == 0


def test_mint_wrong_gauge(accounts, chain, three_cortex_gauges, cortex_minter, token):
    three_cortex_gauges[0].deposit(1e18, {"from": accounts[1]})

    chain.sleep(MONTH)
    cortex_minter.mint(three_cortex_gauges[1], {"from": accounts[1]})

    assert token.balanceOf(accounts[1]) == 0
    assert cortex_minter.minted(accounts[1], three_cortex_gauges[0]) == 0
    assert cortex_minter.minted(accounts[1], three_cortex_gauges[1]) == 0


def test_mint_not_a_gauge(accounts, cortex_minter):
    with brownie.reverts("dev: gauge is not added"):
        cortex_minter.mint(accounts[1], {"from": accounts[0]})


def test_mint_before_inflation_begins(accounts, chain, three_cortex_gauges, cortex_minter, token):
    three_cortex_gauges[0].deposit(1e18, {"from": accounts[1]})

    chain.sleep(token.start_epoch_time() - chain.time() - 5)
    cortex_minter.mint(three_cortex_gauges[0], {"from": accounts[1]})

    assert token.balanceOf(accounts[1]) == 0
    assert cortex_minter.minted(accounts[1], three_cortex_gauges[0]) == 0
