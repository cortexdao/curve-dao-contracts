import brownie

YEAR = 86400 * 365


def test_user_checkpoint(accounts, cortex_gauge):
    cortex_gauge.user_checkpoint(accounts[1], {"from": accounts[1]})


def test_user_checkpoint_new_period(accounts, chain, cortex_gauge):
    cortex_gauge.user_checkpoint(accounts[1], {"from": accounts[1]})
    chain.sleep(int(YEAR * 1.1))
    cortex_gauge.user_checkpoint(accounts[1], {"from": accounts[1]})


def test_user_checkpoint_wrong_account(accounts, cortex_gauge):
    with brownie.reverts("dev: unauthorized"):
        cortex_gauge.user_checkpoint(accounts[2], {"from": accounts[1]})
