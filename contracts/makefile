install:
	@ curl -L https://foundry.paradigm.xyz | bash || true
	@ foundryup
	@ forge install foundry-rs/forge-std OpenZeppelin/openzeppelin-contracts OpenZeppelin/openzeppelin-contracts-upgradeable eth-infinitism/account-abstraction

lint-check:
	@ forge fmt --check

lint-fix:
	@ forge fmt

build:
	@ forge build

type-check:
	@ forge build --force

test:
	@ forge test -vvv

test-fork:
	@ forge test --fork-url $(ETH_RPC_URL) --match-path "test/fork/*.sol" -vvv

deploy:
	@ forge script script/Deploy.s.sol:DeployScript --rpc-url $(ETH_RPC_URL) --broadcast --slow

clean:
	@ forge clean
	@ rm -rf ./cache ./out

.PHONY: *
