
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
	@ forge test --fork-url $(RPC_NODE_URL_4663) --match-path "test/fork/*.sol" -vvv

deploy:
	@ test -n "$${BLOCKSCOUT_API_KEY}" || (printf '%s\n' "BLOCKSCOUT_API_KEY is required for Blockscout verification" >&2; exit 1)
	@ forge script script/Deploy.s.sol:DeployScript --rpc-url "$${RPC_NODE_URL_4663}" --broadcast --slow --verify --verifier blockscout --verifier-url "https://api.blockscout.com/v2/api?chain_id=4663&apikey=$${BLOCKSCOUT_API_KEY}" --etherscan-api-key "$${BLOCKSCOUT_API_KEY}"

clean:
	@ forge clean
	@ rm -rf ./cache ./out

.PHONY: *
