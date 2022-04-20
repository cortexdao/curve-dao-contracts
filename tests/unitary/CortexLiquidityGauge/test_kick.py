import brownie

MAX_UINT256 = 2 ** 256 - 1
WEEK = 7 * 86400


def test_kick(chain, accounts, cortex_gauge, voting_escrow, token, mock_lp_token):
    alice, bob = accounts[:2]
    chain.sleep(2 * WEEK + 5)

    token.approve(voting_escrow, MAX_UINT256, {"from": alice})
    voting_escrow.create_lock(10 ** 20, chain.time() + 4 * WEEK, {"from": alice})

    mock_lp_token.approve(cortex_gauge.address, MAX_UINT256, {"from": alice})
    cortex_gauge.deposit(10 ** 21, {"from": alice})

    assert cortex_gauge.working_balances(alice) == 10 ** 21

    chain.sleep(WEEK)

    with brownie.reverts("dev: kick not allowed"):
        cortex_gauge.kick(alice, {"from": bob})

    chain.sleep(4 * WEEK)

    cortex_gauge.kick(alice, {"from": bob})
    assert cortex_gauge.working_balances(alice) == 4 * 10 ** 20

    with brownie.reverts("dev: kick not needed"):
        cortex_gauge.kick(alice, {"from": bob})
