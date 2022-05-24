from brownie import (
    Contract,
    FeeDistributor,
    accounts,
    history
)

# modify me prior to deployment on mainnet!
DEPLOYER = accounts.at("0xeB47c114B81c87980579340F491f28068E66578d", force=True)

# Protocol SAFE
OWNER_ADMIN = "0x2A208EC9144e6380016aD51a529B354aE1dD5D7d"
# Emergency Safe
EMERGENCY_ADMIN = "0x144Dbd020fe74a4248F87c861551b84aA53A112E"


def main(deployer=DEPLOYER):
    initial_balance = deployer.balance()
    print(f"Deployer address: {deployer}")
    print(f"Deployer balance: {initial_balance/1e18}")
    print("")

    # Tue May 24 20:00:00 EDT 2022 - 2 days before fee collection begins
    start_time = 1653436800

    print("Starting deploy ...")
    print("")
    # deploy the fee distributor
    distributor = FeeDistributor.deploy(
        "0x6021d8e7537d68bcec9a438b2c134c24cbcc1ce3",  # VotingEscrow
        start_time,
        "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490",  # 3Crv
        OWNER_ADMIN,
        EMERGENCY_ADMIN,
        {"from": deployer},
    )
    print("Distributor address:", distributor.address)
    print("")
    print(f"Deployment complete! Total gas used: {sum(i.gas_used for i in history)}")


