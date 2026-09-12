# Agent Barbell — 24 Hour Implementation Plan

Companion to `README.md` (which holds the product thesis and prize research). This file is the **build order**: nine phases, each one a clean, mergeable pull request that moves the whole product forward end-to-end (contract → api → app), never a "backend phase" followed by a "frontend phase".

## Rules for every phase

1. **Copy, don't invent.** Every new file names its closest analogue in `~/Projects/yieldseeker-app`. Open that file first, copy it, then delete what doesn't apply. If you find yourself writing a new pattern, you're probably wrong — go find the yieldseeker equivalent.
2. **Naming translation is mechanical**: `agent_hack` → `agent_barbell`, `AgentManager` → `SystemManager`, `create_agent_manager` → `create_system_manager`, `YieldSeeker*` → `Barbell*`, `yieldSeekerClient` → `agentBarbellClient`. **Env vars follow yieldseeker exactly** — plain names (`GEMINI_API_KEY`, `GRAPH_API_KEY`), chain-suffixed RPC (`RPC_NODE_URL_4663`, `RPC_ARCHIVE_NODE_URL_4663`), and a project prefix *only* where yieldseeker uses `YS_` (so `AB_DEPLOYER_PRIVATE_KEY`, `AB_SERVER_PRIVATE_KEY`). Everything else (camelCase columns with snake_case names, `EntityRepository` aliases, `json_route`-decorated nested endpoint functions, `@kibalabs/ui-react` layout primitives) stays byte-identical in shape.
3. **Every phase ends with a demoable thing.** If a phase can't be shown on screen at its end, it's scoped wrong.
4. **Each phase ends green**: `cd api && make lint-check && make type-check`, `cd app && npx lint && npx type-check`, `cd contracts && make build && make test`.
5. **The deterministic/LLM split is non-negotiable.** From `plans/agent-types-overview.md`, verbatim: *"The agent should translate these instructions into bounded policies. Language-model reasoning must not replace hard transaction, asset, liquidity, or safety controls."* The risk engine sizes and the kill switch fires in Python and Solidity. The LLM only parses intent and narrates. This is also the single strongest judging story we have — don't blur it.

## Timeline at a glance

| Phase | Window | PR | Value delivered | Prizes advanced |
|---|---|---|---|---|
| ✅ P0 | T+0:00 → 1:30 | `chore: accounts, chain config, green pipeline` | Live URLs, all keys in hand | — (unblocks all) |
| P1 | T+1:30 → 4:00 | `feat: AgentWalletKit + RiskBudgetRegistry on Robinhood Chain` | Contracts live on mainnet | Uniswap, Ledger (setup) |
| P2 | T+4:00 → 7:30 | `feat: barbell wallet creation and funded portfolio view` | **User can create + fund a wallet and see it** | Uniswap, Privy-adjacent (flow) |
| P3 | T+7:30 → 11:00 | `feat: substreams context layer and risk engine` | **User sees live vol / momentum / drawdown** | **The Graph ×2 ($10k)** — Route A |
| P4 | T+11:00 → 14:30 | `feat: chat agent and on-chain risk budget policy` | **User sets a risk budget in English** | The Graph AI track |
| P5 | T+14:30 → 18:00 | `feat: swap execution and autonomous kill switch` | **The hero moment — agent defends the budget** | **Uniswap ($3k)**, Chainlink-adjacent |
| P6 | T+18:00 → 19:30 | `feat: mcp server and cross-chain subgraph context` | Other agents can drive Barbell | **Bazantic ($1–2k)**, Graph ×2 — Route B |
| P7 | T+19:30 → 21:00 | `feat: Ledger Key Ring operator signer` | Operator key never in process memory | **Ledger ($3.5k)** |
| P8 | T+21:00 → 24:00 | `docs: submission, demo, docs site` | Submission complete | All |

**Cut lines, in order, if behind:** P7 first (frame Ledger as roadmap), then P6's Route B (Subgraph MCP composition — Route A already qualifies alone), then the rest of P6 (ship the MCP schema without the Bazantic recipe), then P3's 3b (keep RPC ingestion, lose both Graph tracks — this is the expensive one). **Never cut P5** — it is the demo.

---

# Phase 0 — Accounts, chain config, green pipeline — ✅ DONE
**T+0:00 → 1:30.** PR: `chore: accounts, chain config, green pipeline`

Goal: no phase after this one is ever blocked waiting on a signup, a key, or a DNS record. Do all the account work in parallel with one person while the other does the code work.

## Off-code setup

Accounts, keys, funding, GitHub secrets and DNS. Owner: you, not the build. **Done.** `MULTISIG_ADMIN_ADDRESS` was deliberately left empty — admin therefore stays with the deployer key, which is acceptable for the hackathon but weakens the P5 security beat and the P7 trust story.

Two items remain open and are not blockers for P1:

1. **The ETHGlobal continuity question.** Whether a fresh AWK deployment counts as Continuity or Start Fresh changes which pools we submit into. Ask in Discord early.
2. **Whether The Graph actually serves a Substreams endpoint for 4663.** Robinhood is absent from the published endpoint lists; the hostname has to come off The Graph Market. If there isn't one, P3's 3b and both Graph tracks are dead — see Phase 3.

## Chain facts — verified

All verified against 4663 mainnet on 2026-09-12 with `cast` against the public RPC. Nothing here is outstanding.

- ✅ **Uniswap V3 SwapRouter02** — `0xCaf681a66D020601342297493863E78C959E5cb2` (*not* the canonical cross-chain address, which holds unrelated code on 4663; `factory()` and `WETH9()` both revert on it). Its `exactInput` has no `deadline` field, which is exactly what `AWKUniswapV3SwapAdapter` encodes — the adapter vendors across unchanged.
- ✅ **Anchor and satellite assets** — anchor **SGOV** `0x92FD66527192E3e61d4DDd13322Aa222DE86F9B5` at fee 3000 ($2.4M pool depth); satellite **GME** `0x1b0E319c6A659F002271B69dB8A7df2F911c153E` at fee 10000 ($1.06M). Both 18 decimals. Route between them is `[SGOV, USDG, GME]` / fees `[3000, 10000]`.
- ✅ **Base asset** — **there is no USDC on 4663.** It is **USDG** `0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168`, 6 decimals.
- ✅ **Multicall3** — canonical `0xcA11bde05977b3631167028862bE2a173976CA11` is deployed, so `shouldUseMulticall3=True` works.
- ❌ **Subgraphs are not supported on 4663.** Discovered in Subgraph Studio, which contradicts The Graph's own supported-networks docs. Substreams is the only Graph product that reaches this chain — Phase 3 is rewritten around it.

## Implementation

- ✅ **`.github/workflows/api-check.yml`, `app-check.yml`, `api-deploy.yml`, `app-deploy.yml`** — already present and correct (`NAME=agent-barbell-api`, `VIRTUAL_PORT=5100`, `DOMAIN_NAME=agent-barbell.yieldseeker.xyz`, no worker block). Untouched.
- ✅ **`api/agent_barbell/constants.py`** — `ROBINHOOD_CHAIN_ID`, auth-signature constants, `CHAIN_USDG_MAP` / `CHAIN_WETH_MAP` / `CHAIN_ANCHOR_ASSET_MAP` / `CHAIN_SATELLITE_ASSET_MAP`, symbol and decimal maps, `UNISWAP_V3_ROUTER_ADDRESS_MAP`, `SUPPORTED_BASE_ASSETS`, risk-engine bounds, and the `AB_*_ADDRESS_MAP` dicts derived from an empty `AB_DEPLOYMENTS_MAP` that P1 fills in.
- ✅ **`app/src/util/constants.ts`** — Robinhood chain id, RPC, explorer, asset addresses, symbols, decimals, risk-budget defaults. The dead "Sign in with Base" branch was removed from `app/src/pages/HomePage.tsx`.
- ✅ **`api/agent_barbell/create_system_manager.py` + `system_manager.py` + `user_manager.py` + `eth_client_manager.py`** — the central `SystemManager`, following `create_agent_manager.py`'s four-function shape (`create_` / `setup_` / `teardown_` / `use_`). `SystemManager` *is* the `SignatureAuthorizer`, exactly as `AgentManager` is; the standalone `auth.py` was deleted. `application.py` builds it at module level and `DatabaseConnectionMiddleware` takes `systemManager.userManager.database`. `pyproject.toml` gained the `requester` extra, which was missing.
- ✅ **`api/tests/__init__.py`** — the makefile lints `./tests` and the directory did not exist, so `api-check.yml` was red on every PR.

**Done when:** ✅ `make lint-check` / `make type-check` pass in `api/`, `npx lint` / `npx type-check` / `make build` pass in `app/`, and `application.py` imports with `SystemManager` wired. ⬜ Remaining: confirm a push to `main` deploys, `https://agent-barbell-api.yieldseeker.xyz/health` returns ok, `https://agent-barbell.yieldseeker.xyz` loads, and SIWE login creates a user row in `barbelldb`.

---

# Phase 1 — AgentWalletKit + RiskBudgetRegistry on Robinhood Chain
**T+1:30 → 4:00.** PR: `feat: AgentWalletKit + RiskBudgetRegistry on Robinhood Chain`

Goal: a fresh, independent AWK deployment on 4663, plus the one new contract this product needs. This is deliberately early: contract addresses are the input to the Subgraph (P3) and the api (P2), and a mainnet deploy that goes wrong at hour 18 kills the project.

## Off-code setup

- Deployer EOA funded with 4663 gas (from P0 step 2 — confirm it landed).
- Robinhood Chain block explorer verification: find the explorer's Etherscan-compatible verify endpoint and API key, or accept unverified contracts and show source in the repo. Verified contracts materially help judging on the Uniswap and Ledger tracks — spend 10 minutes here.

## Implementation

- **`contracts/` scaffold** — new directory. Copy `yieldseeker-app/contracts/foundry.toml` (solc `0.8.28`, cancun, optimizer 200, `via_ir`, OZ/upgradeable/forge-std/account-abstraction remappings, `fs_permissions` read-write `./`, fmt line 240) and `yieldseeker-app/contracts/makefile` (`install` = foundryup + forge install; `build`; `test` = `forge test -vvv`; `test-fork`; `type-check` = `forge build --force`; `clean`) verbatim. Add `lint-check`/`lint-fix` = `forge fmt --check` / `forge fmt` from `contracts-internal/makefile`.
- **`contracts/src/agentwalletkit/**`** — vendor the AWK core unchanged from `yieldseeker-app/contracts/src/agentwalletkit/`: `AWKAdapter.sol`, `AWKAdapterRegistry.sol`, `AWKAgentWalletFactory.sol`, `AWKAgentWalletProxy.sol`, `AWKAgentWalletV1.sol`, `AWKErrors.sol`, plus `adapters/AWKSwapAdapter.sol` and `adapters/AWKUniswapV3SwapAdapter.sol` from the nested `adapters/` subdirectory. **Do not edit these** — byte-identical vendoring is what makes the eventual merge back into yieldseeker trivial, and it's the honest continuity story.
- **`contracts/src/adapters/BarbellUniswapV3SwapAdapter.sol`** — copy `yieldseeker-app/contracts/src/adapters/UniswapV3SwapAdapter.sol` (`YieldSeekerUniswapV3SwapAdapter`, ctor `(router, sellPolicy)`, `_beforeSwap` sell-policy + base-asset validation, `_afterSwap` fee recording). **Strip the `FeeTracker` call** — we charge no fees in a hackathon build, and the tracker is dead weight. Keep `_beforeSwap`'s policy validation: it is the contract-level guardrail the P5 security demo depends on.
- **`contracts/src/adapters/BarbellSellPolicy.sol`** — copy `yieldseeker-app/contracts/src/adapters/SwapSellPolicy.sol` (`YieldSeekerSwapSellPolicy`: AccessControl + EnumerableSet, `addSellableToken`, `removeSellableToken`, `validateSellableToken`, `error SellTokenNotAllowed(address token)`). Seed with anchor (SGOV), satellite (GME) and USDG only. This is what makes "send all my USDG to this address" fail on-chain.
- **`contracts/src/RiskBudgetRegistry.sol`** — the one genuinely new contract. Model it on `SwapSellPolicy.sol`'s shape (AccessControl, small state, event-per-mutation) — that's the house pattern for "a registry whose real product is its event log".
  - State: `mapping(address wallet => Policy)` where `Policy { uint16 maxDrawdownBps; uint16 targetSatelliteBps; uint16 maxSatelliteBps; uint64 updatedAt; bool isKilled; }`.
  - `setPolicy(address wallet, Policy calldata policy)` — callable by the wallet owner only.
  - `recordKillSwitch(address wallet, uint16 drawdownBps, uint16 newSatelliteBps, string calldata reason)` — callable by the registered operator only.
  - `clearKillSwitch(address wallet)` — **owner only, never the operator, never the LLM.** Re-arming is a human decision.
  - Events, following `SwapSellPolicy`'s `event SellableTokenAdded(address indexed token);` style: `event PolicyUpdated(address indexed wallet, uint16 maxDrawdownBps, uint16 targetSatelliteBps, uint16 maxSatelliteBps);` `event KillSwitchTriggered(address indexed wallet, uint16 drawdownBps, uint16 newSatelliteBps, string reason);` `event KillSwitchCleared(address indexed wallet);` `event SatelliteResized(address indexed wallet, uint16 fromBps, uint16 toBps, string reason);`
  - Errors: `NotWalletOwner()`, `NotOperator()`, `InvalidPolicy()`.
- **`contracts/script/Deploy.s.sol`** — copy `yieldseeker-app/contracts/script/Deploy.s.sol` (440 lines) and cut it down hard. Keep: the `getUniswapV3Router(uint256 chainId)` helper shape with its `if (chainId == ...) return <addr>; revert(string.concat("Unsupported chain id for ...: ", vm.toString(chainId)));` body — just swap `8453` for `4663`; the `SERVER_ADDRESS`/`DEPLOYER_PRIVATE_KEY`/`MULTISIG_ADMIN_ADDRESS` env reads; the `safeReadAddress` idempotent-redeploy pattern against `deployments.json`; the CREATE2 salt. **Use a different salt from `0x711`** so addresses can't collide with a yieldseeker deployment. Delete every Aave/Compound/ERC4626/Merkl/Moonwell/Aerodrome/FeeTracker/timelock branch.
- **`contracts/deployments.json`** — same flat `{"key": "0x..."}` shape as yieldseeker's. Keys: `adapterRegistry`, `agentWalletFactory`, `agentWalletImplementation`, `uniswapV3SwapAdapter`, `sellPolicy`, `riskBudgetRegistry`.
- **`contracts/test/unit/RiskBudgetRegistry.t.sol`** — forge-std `Test`, `setUp` deploying the registry, following `contracts-internal/test/unit/ProBilling.t.sol`. Cover: owner-only `setPolicy`, operator-only `recordKillSwitch`, **operator cannot `clearKillSwitch`**, `InvalidPolicy` on `targetSatelliteBps > maxSatelliteBps`.
- **`contracts/test/fork/BarbellSwap.t.sol`** — copy the fork-test convention from `yieldseeker-app/contracts/test/fork/` (skip unless forked to the right chain id). Forks 4663, deploys the adapter, executes one real anchor→satellite swap through a wallet. **This test is what de-risks P5** — if the router address or fee tier is wrong, you find out here at hour 4, not at hour 17.

**Done when:** `make test` and `make test-fork` pass, `deployments.json` has six real 4663 addresses, and `cast call` against `riskBudgetRegistry` returns an empty policy for a fresh address.

---

# Phase 2 — Barbell wallet creation and funded portfolio view
**T+4:00 → 7:30.** PR: `feat: barbell wallet creation and funded portfolio view`

Goal: **the first phase a stranger can look at and understand.** A user signs in, gets an AWK wallet on Robinhood Chain, deposits USDG, and sees their anchor/satellite/cash split on screen. No risk logic yet, no LLM. Just: it's real, it holds real money, it shows real balances.

## Off-code setup

- Fund the demo user wallet with USDG on 4663 (from P0). Do one manual `anchor` buy on the Robinhood Chain Uniswap UI so the demo account has a non-trivial position to display.
- Confirm the public RPC actually serves 4663 `eth_getLogs` with a wide block range — the P3 Subgraph is the real indexer, but `RpcClient` needs logs to work for the fallback path.

## Implementation — api

- **`api/agent_barbell/eth_client_manager.py`** — copy `api/agent_hack/eth_client_manager.py` (61 lines) verbatim: `ThrottledRestEthClient` with its module-level `_RPC_SEMAPHORE = asyncio.Semaphore(10)` and `get_code`, plus `EthClientManager` with `register_client`/`register_archive_client`/`get_regular_client`/`get_archive_client`. Drop `register_paymaster_client` — no paymaster on 4663.
- **`api/agent_barbell/barbell_abis.py`** — copy the relevant slices of `api/agent_hack/yieldseeker_abis.py` (495 lines): `AGENT_WALLET_FACTORY_ABI` (`createAgentWallet`, `getAddress`, `listAgentOperators`), `AGENT_WALLET_ABI` (`executeViaAdapter`, `executeViaAdapterBatch`, withdrawals), `ADAPTER_REGISTRY_ABI` (`getAllTargets`, `getTargetAdapter`), `ERC20_ABI` from `api/agent_hack/yield_providers/erc_abis.py`. Add a hand-written `RISK_BUDGET_REGISTRY_ABI` for the P1 contract. Hand-maintained ABI constants in Python is the yieldseeker convention — do not add a codegen step.
- **`api/agent_barbell/blockchain_data/blockchain_data_client.py`** — copy `api/agent_hack/blockchain_data/blockchain_data_client.py` (78 lines): the abstract `BlockchainDataClient` and the `ClientAsset` / `ClientAssetBalance` / `ClientAssetPrice` / `ClientWalletErc20Transfer` models.
- **`api/agent_barbell/blockchain_data/rpc_client.py`** — copy `api/agent_hack/blockchain_data/rpc_client.py` (103 lines) nearly verbatim: `RpcClient(BlockchainDataClient)`, `get_wallet_asset_balances` (native via `eth_getBalance`, ERC20 via `call_function_by_name` + `ERC20_ABI`, `asyncio.gather`, filter zero balances), `list_wallet_erc20_transfers` with the `TRANSFER_EVENT_TOPIC` constant. Skip `AlchemyClient`/`MoralisClient`/`RoutingBlockchainDataClient` — one chain, one client, no routing layer to justify yet.
- **`api/agent_barbell/adapter_registry_manager.py`** — copy `api/agent_hack/adapter_registry_manager.py` (102 lines) verbatim, including the `DictCache` + `asyncio.Lock` refresh and the `multicall(contractCalls, shouldUseMulticall3=True)` fan-out over `getAllTargets` → `getTargetAdapter`. Point `_get_registry_address` at `constants.AB_ADAPTER_REGISTRY_ADDRESS_MAP`.
- **`api/agent_barbell/transaction_manager.py`** — copy `api/agent_hack/transaction_manager.py` (515 lines), keeping `TransactionFailedException` (imported by `chat_tool.py` in P4), nonce handling, gas estimation, receipt polling, and `tbl_transactions` persistence. Cut the CDP/bundler/userop paths — we sign with a plain EOA operator key on 4663.
- **`api/agent_barbell/wallet_manager.py`** — new manager, modelled on `api/agent_hack/create_agent_manager.py` (616 lines) collapsed to its essentials. `WalletManager.create_barbell_wallet(userId)` calls `createAgentWallet` on the factory with the user as owner and our operator as operator, persists a `Barbell` row; `get_wallet_address(userId)`; `deposit_instructions(...)`.
- **`api/agent_barbell/portfolio_manager.py`** — new, modelled on `api/agent_hack/asset_manager.py` (501 lines). `get_portfolio(barbellId)` → balances from `RpcClient` + USD prices, classified into `anchor` / `satellite` / `cash` legs, with `satelliteBps` and `totalValueUsd`. This is the single most reused method in the codebase — get its return shape right now.
- **`api/agent_barbell/model.py`** — extend the existing file (currently `User`, `AuthToken`) with `Barbell`, `BarbellPolicy`, `RiskSnapshot`, `BarbellAction`, `ChatEvent`, following `api/agent_hack/model.py` (1,049 lines) — plain Pydantic `BaseModel`s, camelCase fields, no ORM.
- **`api/agent_barbell/store/schema.py`** — extend with `BarbellsTable`/`BarbellsRepository`, `BarbellPoliciesTable`, `RiskSnapshotsTable`, `BarbellActionsTable`, `ChatEventsTable`, each with the paired `XRepository = EntityRepository(table=XTable, modelClass=X)` alias, exactly as `api/agent_hack/store/schema.py` (878 lines) does. camelCase `key=`, snake_case `name=`.
- **`api/alembic/versions/`** — one migration, named `<timestamp>-<rev>_add_barbell_tables.py`, matching the existing `2026_09_07_1357-fe3425a78026_create_users_table.py` and the yieldseeker header format (docstring with Revision ID / Revises / Create Date, then `revision`/`down_revision`, then `upgrade`/`downgrade`).
- **`api/agent_barbell/api/v1_api.py`** — extend `create_v1_routes` with nested `@json_route`-decorated functions, following `api/agent_hack/api/v1_api.py` (1,471 lines): `create_barbell` (POST `/barbells`), `get_barbell` (GET `/barbells/{barbellId}`), `get_barbell_portfolio` (GET `/barbells/{barbellId}/portfolio`). Copy `api/agent_hack/api/route_decorators.py` (77 lines) and `rate_limit_decorator.py` (101 lines) at the same time.
- **`api/agent_barbell/api/endpoints.py` / `resources.py` / `resource_builder.py`** — the skeleton has `endpoints.py` but no resources layer. Add it now, following `api/agent_hack/api/v1_endpoints.py` (1,032), `v1_resources.py` (671) and `v1_resource_builder.py` (649): endpoints are thin request/response Pydantic models, `resources.py` holds the API-shaped domain types, and `ResourceBuilderV1` converts model → resource. Do not let managers return API resources directly.
- **`api/application.py`** — extend the existing wiring. Follow `yieldseeker-app/api/application.py`'s ordering: build clients → build managers → build `ResourceBuilderV1` → mount routes. Add an `api/agent_barbell/create_barbell_manager.py` factory exposing `create_barbell_manager()` and `use_barbell_manager()`, copied from `api/agent_hack/create_agent_manager.py`'s factory + `@asynccontextmanager` pattern, and call it from `lifespan`.

## Implementation — app

- **`app/src/client/{client.ts,endpoints.ts,resources.ts,index.ts}`** — **replace the hand-written `fetch` wrapper in the skeleton.** Copy the structure of `yieldseeker-app/app/src/client/`: `AgentBarbellClient extends ServiceClient` with `getHeaders(authToken)` setting `Content-Type`, `skip_zrok_interstitial` and `Authorization: Signature ...`; `endpoints.ts` with `RequestData`/`ResponseData` subclasses and their `toObject`/`fromObject`; `resources.ts` with typed domain classes. The skeleton's own comment says to swap to `ServiceClient` "once there are enough endpoints" — that's now, and doing it later means rewriting every call site.
- **`app/src/BarbellContext.tsx`** — copy `yieldseeker-app/app/src/AgentsContext.tsx` (185 lines): provider + `useBarbell()` hook, route-param driven, redirecting when the id is invalid.
- **`app/src/app.tsx`** — add `QueryClientProvider` + `ReactQueryDevtools` and `PageDataProvider` to match yieldseeker's exact nesting order (`KibaApp > PageDataProvider > GlobalsProvider > QueryClientProvider > Router > Web3AccountControlProvider > AuthProvider > BarbellProvider > ContainingView > SubRouter`). Add routes `/barbell/overview`, `/barbell/fund`.
- **`app/src/components/ContainingView.tsx`** — the skeleton's is a stub. Grow it toward `yieldseeker-app/app/src/components/ContainingView.tsx` (798 lines): navbar, connect/login gate, authenticated shell. Take the shell and nav, leave the agent chooser and pro banners.
- **`app/src/components/PortfolioView.tsx`** — new. Copy the card/stat layout idioms from `yieldseeker-app/app/src/components/PerformanceView.tsx` (554 lines) and reuse `AnimatedNumber.tsx` (66) and `IncrementingNumberView.tsx` (73) verbatim. Renders the barbell as two labelled bars — anchor vs satellite — plus total value.
- **`app/src/components/DepositForm.tsx`** — copy `yieldseeker-app/app/src/components/DepositForm.tsx` (217 lines) almost verbatim; it already does amount input + approve + transfer against a wallet address.
- **`app/src/pages/BarbellOverviewPage.tsx`, `FundBarbellPage.tsx`** — copy `yieldseeker-app/app/src/pages/FundAgentPage.tsx` (291) and the overview page structure. Delete `DashboardPage.tsx` from the skeleton and redirect `/dashboard` → `/barbell/overview`.
- **`app/src/components/LoadingIndicator.tsx`, `Tooltip.tsx`** — copy verbatim (16 and 17 lines). Free consistency.

**Done when:** on the deployed URL, sign in with a wallet → "Create your barbell" → an AWK wallet address appears → deposit USDG → the portfolio view shows the real balance within one refresh.

---

# Phase 3 — Substreams context layer and risk engine
**T+7:30 → 11:00.** PR: `feat: substreams context layer and risk engine`

Goal: the intellectual core of the product, and Route A of the Graph strategy. **Every number the agent reasons about is derived from indexed history, not ad-hoc RPC math**, and the pipeline that produces it is a reusable, composable Substreams module.

**Subgraphs are not available on Robinhood Chain.** Subgraph Studio rejects 4663 outright ("Subgraphs no longer supported on Robinhood Chain… You can use Substreams to receive data from Robinhood Chain"), despite what `thegraph.com/docs/en/supported-networks/robinhood/` still claims. Substreams is the only Graph product that reaches this chain, and both Graph tracks accept it:

- **Composability ($5k)** — verbatim qualification: *"Authoring or extending a Standardized Subgraph, **or contributing a reusable composable Substreams module**, is in scope"*, and the brief opens with *"compose reusable Substreams packages into new pipelines"*. Live-data requirement is met by *"The Graph Market for Substreams"*.
- **AI Tooling / AI Use Case, From Scratch pool ($5k)** — *"stream data with Substreams"*, plus a **featured challenge**: *"use the Substreams SKILLS to go from a single natural-language prompt to a working, deployed Substreams pipeline."*

## Build order within the phase — this matters

Do **3a before 3b.** The risk engine reads price ticks and snapshots from **our Postgres**, so the ingestion source is a swappable detail. Build RPC ingestion first (~1h, we control the contracts and the volume is trivial), get the whole vertical slice working, then repoint ingestion at Substreams. If Substreams eats an afternoon, you still have a demo; if it lands, you have $10k of prize surface. Going straight at Substreams risks hour 12 with no data layer at all.

## Off-code setup

- **Try the Substreams SKILL first**, before hand-rolling anything: it is both the cheapest path through the Rust and an explicitly featured judging item. Fall back to `substreams init` with an EVM "events for contract address" template, which scaffolds the module without hand-written Rust.
- The Graph Market account + auth token for consuming the deployed package live. Studio is irrelevant now — do not waste time there.
- Index from the **P1 deployment block**, not genesis. Sync time on a 100ms-block chain is a live-demo risk.

## Implementation — 3a, ingestion and the engine

- **`api/agent_barbell/store/schema.py`** — add `PriceTicksTable`/`PriceTicksRepository` alongside the `RiskSnapshotsTable` from P2, with the paired `EntityRepository` alias convention.
- **`api/agent_barbell/block_manager.py`** — copy `api/agent_hack/block_manager.py` (98 lines) verbatim; the ingestion loop needs block-number-at-date lookups and it is already tested in yieldseeker.
- **`api/agent_barbell/ingestion_manager.py`** — new manager. Reads `Swap` logs from the two Uniswap pools and the four `RiskBudgetRegistry` events via `RpcClient.list_wallet_erc20_transfers`'s `eth_getLogs` pattern, derives `PriceTick` rows from swap amounts, upserts through `PriceTicksRepository.upsert_many`. Follows the manager conventions of `api/agent_hack/stats_manager.py` (1,072 lines). **This class is the seam** — 3b replaces its source, not its output.
- **`api/agent_barbell/risk_engine.py`** — new, and **deterministic by design**. Modelled structurally on `api/agent_hack/rule_compiler.py` (319 lines) — pure functions over inputs, no I/O, fully unit-testable.
  - `calculate_realized_volatility(priceTicks, windowDays)` — rolling stdev of log returns, annualised. Simplest formula that's demo-legible.
  - `calculate_momentum(priceTicks, windowDays)` — sign and magnitude of trailing return.
  - `calculate_drawdown_from_peak(snapshots)` — the number the whole product defends.
  - `calculate_target_satellite_bps(policy, volatility, momentum, drawdownBps)` — volatility targeting, momentum overlay, clamped to `policy.maxSatelliteBps`, forced to zero when `drawdownBps >= policy.maxDrawdownBps`.
  - `RiskState` result model carrying every intermediate so the UI and the LLM can both explain the decision. Borrow the `decisionTrace` idea from `plans/agent-type-borrowing.md`.
- **`api/agent_barbell/risk_manager.py`** — new manager, orchestration only: read ticks and snapshots from the repositories, call `risk_engine`, persist a `RiskSnapshot`. Registered on `SystemManager` in `create_system_manager.py`.
- **`api/tests/test_risk_engine.py`** — copy the fixture style of `yieldseeker-app/api/tests/test_block_manager.py`. **The engine tests need no database at all** — pure functions in, expected numbers out. Cover: flat prices → near-zero vol; a 20% crash → drawdown crosses the budget → `calculate_target_satellite_bps` returns `0`. **These are the only tests that must exist in this build** — they defend the one claim the whole pitch rests on.
- **`api/agent_barbell/api/v1_api.py`** — add `get_risk_state` (GET `/barbells/{barbellId}/risk-state`).
- **`app/src/components/RiskStateView.tsx`** — new. Copy the chart setup from `yieldseeker-app/app/src/components/PerformanceView.tsx` (554 lines, recharts `^3.10.1`). Shows drawdown-from-peak against the budget line, realized vol, momentum, and the engine's current target satellite size. Reuse `TierProgressBar.tsx` (98 lines) for the "distance to your budget" bar — already themed, exactly the right visual.
- **`app/src/pages/BarbellOverviewPage.tsx`** — mount `RiskStateView` above `PortfolioView`.

## Implementation — 3b, swap ingestion to Substreams

- **`substreams/`** — new top-level directory, treated as a peer service exactly like `yieldseeker-app/xmtp-api/` and `card-renderer/`: its own `makefile` (`install`/`build`/`deploy`/`run` targets in the style of `card-renderer/makefile`), `substreams.yaml`, and `proto/`. No `Dockerfile` — it deploys to The Graph Market, not the appbox.
  - **Compose, don't rewrite.** Take a published Uniswap V3 Substreams package as an **input module** and write one `barbell_risk` module on top that emits anchor/satellite price ticks plus `RiskBudgetRegistry` events. Composing packages into a new pipeline is the composability brief's opening sentence, and it's less work than indexing pools from scratch.
  - **Publish `barbell_risk` to The Graph Market** as a reusable module. "Contributing a reusable composable Substreams module" is the qualification bullet; publishing is what makes it true rather than claimed.
- **`api/agent_barbell/substreams_sink.py`** — new. Consumes the deployed package and writes the same `PriceTicksRepository` rows `IngestionManager` was writing. Nothing downstream changes.
- **Delete the RPC ingestion path only if Substreams is stable.** Keeping it as a fallback behind a flag is fine and costs nothing; the *reasoning* path must read from the ingested tables either way.

**Done when:** the overview page renders live vol/momentum/drawdown from ingested history, `test_risk_engine.py` proves the kill-switch threshold in isolation, and (3b) `barbell_risk` is deployed and consumed live from The Graph Market.

---

# Phase 4 — Chat agent and on-chain risk budget policy
**T+11:00 → 14:30.** PR: `feat: chat agent and on-chain risk budget policy`

Goal: the natural-language front door. *"Anchor in treasuries, satellite in GME, never let this account lose more than 15% from its peak"* → a structured policy → an on-chain `PolicyUpdated` event → a plain-English confirmation.

## Off-code setup

- `GEMINI_API_KEY` live and rate limits checked.
- Optional: `OPENROUTER_API_KEY` for Hermes. **Timebox any Hermes work to 20 minutes** — if function-calling misbehaves, ship Gemini and mention Hermes as pluggable.

## Implementation

- **`api/agent_barbell/agent/chat_bot.py`, `chat_tool.py`, `chat_history_store.py`, `chat_event.py`, `runtime_state.py`** — copy from `api/agent_hack/agent/` (71, 49, 62, and 34 lines) **verbatim**. The `LLM` abstract base, the `ChatBot.execute()` async generator with its `AGENT_CHAT_MAX_STEPS` runaway guard, the `ChatTool[ParamsType, RuntimeStateType]` generic with its `execute()` exception envelope and `model_to_markdown_yaml` helpers — all of it applies unchanged. This is the highest copy-leverage in the whole plan: a working tool-calling agent loop for ~220 lines of copied code.
- **`api/agent_barbell/agent/gemini_llm.py`** — copy `api/agent_hack/agent/gemini_llm.py` (56 lines) verbatim.
- **`api/agent_barbell/agent/barbell_runtime_state.py`** — copy `api/agent_hack/agent/ys_runtime_state.py` (34 lines); carries `userId`, `barbellId`, `conversationId`.
- **`api/agent_barbell/agent/tools/`** — one file per tool, each copied from its nearest yieldseeker sibling:
  - `get_portfolio_tool.py` ← `agent/tools/get_balances_tool.py` (25 lines)
  - `get_risk_state_tool.py` ← `agent/tools/get_vault_historic_metrics_tool.py` (75 lines)
  - `set_risk_budget_tool.py` ← `agent/tools/update_rule_preset_tool.py` (41 lines) — parses NL into a `BarbellPolicy` and writes `setPolicy` on-chain
  - `get_policy_tool.py` ← `agent/tools/get_effective_rules_tool.py` (87 lines)
  - `get_history_tool.py` ← `agent/tools/get_historical_performance_tool.py` (80 lines)
  - `explain_last_action_tool.py` ← `agent/tools/get_autoseek_decisions_tool.py` (121 lines)
  - **No tool sizes a trade and no tool clears the kill switch.** `set_risk_budget_tool` writes bounds; the engine acts within them. If a reviewer can find an LLM path to an unbounded trade, the pitch collapses.
- **`api/agent_barbell/conversation_manager.py`** — copy `api/agent_hack/conversation_manager.py` (510 lines), trimmed: conversation creation, event persistence to `tbl_chat_events`, history windowing.
- **`api/agent_barbell/api/v1_api.py`** — add `add_user_message` as a `@streaming_json_route` (POST `/barbells/{barbellId}/messages`) and `list_chat_events` (GET). Copy the streaming endpoint shape from yieldseeker's `add_user_message` / `add_guest_user_message`.
- **`api/agent_barbell/prompts.py`** — new, following `api/agent_hack/messages.py` (49 lines) + the system-prompt strings in `agent_manager.py`. The system prompt must state the boundary explicitly: the model translates intent into bounded policy and narrates engine output; it never sizes positions and never overrides the kill switch.
- **`app/src/client/client.ts`** — add `addUserMessageStreamed`, copying yieldseeker's `fetch` + `ReadableStream` reader + newline-delimited JSON + `Resources.ChatStreamEvent.fromObject` implementation verbatim.
- **`app/src/components/ChatView.tsx`** — copy `yieldseeker-app/app/src/components/ChatView.tsx` (325 lines) including its `@kibalabs/ui-react` `Markdown` rendering and suggestion chips. Copy `LoadingIndicatorChat.tsx` (16 lines) with it.
- **`app/src/components/RiskBudgetPresetSelector.tsx`** — copy `yieldseeker-app/app/src/components/RulePresetSelector.tsx` (41 lines). Three presets — Conservative 10% / Balanced 15% / Aggressive 25% — so a judge who won't type a sentence still gets the point in one click.
- **`app/src/components/PolicyPanel.tsx`** — copy `yieldseeker-app/app/src/components/AgentCompiledRulesPanel.tsx` (111 lines). Shows the active on-chain policy with a link to the `PolicyUpdated` tx. Making the promise verifiable on-chain is half the product.
- **`app/src/pages/ChatPage.tsx`** — copy `yieldseeker-app/app/src/pages/ChatPage.tsx` (225 lines).

**Done when:** typing the demo sentence produces a `PolicyUpdated` event on 4663, the `PolicyPanel` reflects it, and the agent answers "what's my risk state right now" from Graph data.

---

# Phase 5 — Swap execution and the autonomous kill switch
**T+14:30 → 18:00.** PR: `feat: swap execution and autonomous kill switch`

Goal: **the hero moment.** Everything before this is a dashboard with a chatbot. This is the phase where the agent actually defends money. Do not let it get squeezed.

## Off-code setup

- Operator EOA funded with gas and registered as operator on the demo wallet.
- **Build the market-move rehearsal before you need it.** Two options, decide now: (a) execute a real oversized satellite sell on the live pool to move the mark, or (b) a `--simulate` flag on the worker that injects a synthetic price series into the risk engine. **Do both.** (b) is the reliable demo; (a) is the honest proof. A live demo that depends on the market moving on cue will not move on cue.
- Record a screen capture of a successful kill-switch run the moment one works. That recording is your fallback if the venue wifi dies.

## Implementation

- **`api/agent_barbell/execution_manager.py`** — new, the deterministic actuator. Modelled on `api/agent_hack/autoseek_manager.py` (1,038 lines) for its decide-then-execute loop, and `api/agent_hack/yieldseeker_swap_policy_manager.py` (121 lines) for pre-trade policy checks.
  - `resize_satellite(barbellId, targetSatelliteBps, reason)` — reads the portfolio, computes the delta, builds the `SwapRoute { address[] path; uint24[] fees }` for the AWK adapter, calls `executeViaAdapter` through `TransactionManager`, records a `BarbellAction`.
  - `trigger_kill_switch(barbellId, drawdownBps, reason)` — resize satellite to zero, then `recordKillSwitch` on `RiskBudgetRegistry`. Idempotent: never fires twice for the same episode.
  - **Threshold-based, not continuous.** From `plans/agent-type-rebalancing.md`, verbatim: *"Research favors frequent monitoring with relatively infrequent threshold-based trades; trading every small fluctuation creates unnecessary cost and tax events."* Monitor every minute; trade only when the drift exceeds a rebalance band or the kill switch fires. A judge who sees the agent churn every tick will read it as unserious.
- **`cron/`** — new top-level service. Copy `yieldseeker-app/cron/worker.py` (9.6KB) near-verbatim: the `CronJob` / `ApiRequestCronJob` Pydantic models, the `CronExecutor` with `AsyncIOScheduler`, `IntervalTrigger(start_date=<2025-01-01 UTC>, jitter=...)`, `add_job(replace_existing=True)`, and the `Requester` lifecycle. Also copy `cron/pyproject.toml`, `cron/makefile`, `cron/Dockerfile`. Jobs:
  - `barbell-risk-check` — every 1 minute → POST `/v1/cron/risk-check`
  - `barbell-snapshot` — every 15 minutes → POST `/v1/cron/snapshot`
- **`api/agent_barbell/api/v1_api.py`** — add cron-token-authorised routes `/cron/risk-check` and `/cron/snapshot`, using the `StaticTokenAuthorizer` pattern from `yieldseeker-app/api/agent_hack/api/v1_api.py` and a `CRON_API_SECRET`.
- **`.github/workflows/api-deploy.yml`** — restore the worker `docker run` block from yieldseeker's workflow (`/bin/bash -c 'make start-worker'`, same `--env-file ~/.agent-barbell-api.vars`).
- **`api/tests/test_execution_manager.py`** — fake `TransactionManager`, assert the kill switch produces exactly one sell of exactly the right size and exactly one `recordKillSwitch` call, and that a second invocation in the same episode is a no-op.
- **`app/src/components/ActionTimeline.tsx`** — new. Copy `yieldseeker-app/app/src/components/AgentMemoriesPanel.tsx` (486 lines) for its card-list-with-detail idiom. Each entry: what the engine saw, what it did, the tx link. **This is the component judges will actually read** — it's the audit trail that proves the narration matches the chain.
- **`app/src/components/KillSwitchSimulationDialog.tsx`** — copy `yieldseeker-app/app/src/components/SimulationDialog.tsx` (532 lines). Drives the `--simulate` path: pick a shock size, watch the engine cross the budget and act. This is your on-stage button.
- **`app/src/components/GlowingBanner.tsx`** — copy verbatim (51 lines). Renders the armed/triggered kill-switch state at the top of the overview page.
- **Security proof (do not skip).** Add a demo path where the chat agent is asked to send USDG to an arbitrary address. There is no tool that can do it; if a judge insists, show the raw `executeViaAdapter` call against an unregistered target reverting with AWK's `AdapterNotRegistered` / `TargetNotRegistered`, and the sell-policy revert `SellTokenNotAllowed(address)`. Record the failing tx hash in the README's security section. A compromised LLM still can't move funds outside policy — say it, then prove it with a hash.

**Done when:** the simulated shock drives the engine across the budget, the satellite leg is actually sold on Robinhood Chain Uniswap, `KillSwitchTriggered` is on-chain, and the timeline and chat both explain it — with no human in the loop.

---

# Phase 6 — MCP server and cross-chain Subgraph MCP context
**T+18:00 → 19:30.** PR: `feat: mcp server and cross-chain subgraph context`

Goal: the Bazantic prize, the "AI tooling" half of the Graph AI track, and **Route B of the Graph strategy** — a second Graph product composed alongside the P3 Substreams pipeline. Cheap, because every tool below is a thin wrapper over a manager that already exists.

**Route B is the optional half.** Route A (P3) already qualifies for the composability track on its own via the reusable Substreams module. Route B strengthens it to the first qualification bullet — *"compose two or more of The Graph's products"* — but only counts if the second product genuinely feeds a decision. A benchmark query we don't act on reads as padding, and *"show what became easier because a shared schema or composed product was used"* is an explicit judging criterion. If it can't be wired into the engine honestly, ship Route A alone and say so.

## Off-code setup

- Bazantic account (P0 step 12); register the Barbell API and author a Recipe.
- Capture a **before/after** transcript: an agent trying to reason about a Robinhood Chain barbell with raw RPC access vs. with the Barbell MCP. Bazantic's brief explicitly asks you to *prove* the improvement — a side-by-side transcript is the proof.

## Implementation

- **`mcp/`** — new top-level Node service, structured exactly like `yieldseeker-app/xmtp-api/`: `package.json`, `tsconfig.json`, `Dockerfile`, `makefile`, `src/index.ts` with env validation at boot (`API_BASE_URL`, `MCP_API_TOKEN`) in the same style as xmtp-api's startup validation. Deploys as another `docker run` on the appbox at `agent-barbell-mcp.yieldseeker.xyz`.
- **`mcp/src/tools/*.ts`** — `get_portfolio`, `get_risk_state`, `set_risk_budget`, `execute_rebalance`, `get_action_history`. Each one is an HTTP call to the v1 API — **no business logic in the MCP layer.** Adding a context source must remain a schema change, not new integration code.
- **`api/agent_barbell/api/mcp_api_v1.py` + `mcp_endpoints_v1.py` + `mcp_resources_v1.py`** — copy the whole three-file integrator pattern from `api/agent_hack/api/{sdk_api_v1.py,sdk_endpoints_v1.py,sdk_resources_v1.py}` (131 / 120 / 144 lines) and `api/agent_hack/sdk_manager.py` (447 lines). Mount at `/mcp/v1` alongside `/v1`, token-authorised. yieldseeker already solved "expose a narrower, token-authorised surface for machines" — reuse it rather than exposing `/v1` with a second auth mode.
- **`api/agent_barbell/external/subgraph_mcp_client.py`** — **Route B.** New, following the external-client convention of `api/agent_hack/external/merkle_client.py` (438 lines): constructor takes a kiba-core `Requester`, methods return typed Pydantic response models, no raw dicts escape. Queries the official Subgraph MCP for context 4663 cannot provide — Uniswap subgraphs on mainnet/Base carrying the *same* underlyings, used as a cross-chain volatility benchmark. Wire the result into `risk_engine.calculate_realized_volatility` as a sanity bound (our chain is young and thin; a 14-day window there is noisy), so the composed product changes a real number rather than decorating the UI.

**Done when:** an external MCP client (Claude Desktop or the Bazantic runner) lists the five tools, reads a live risk state, and sets a risk budget end-to-end — and, if Route B shipped, `get_risk_state` returns a volatility figure that provably differs because of the cross-chain benchmark.

---

# Phase 7 — Ledger Key Ring operator signer
**T+19:30 → 21:00.** PR: `feat: Ledger Key Ring operator signer`

Goal: the Ledger prize ($3.5k). The brief is "hardware-backed secrets an agent can't leak" plus "human-in-the-loop approval for high-risk actions" — and our architecture already separates a low-risk operator path from high-risk owner-only actions. This phase makes that split physical rather than conceptual.

**Cut this first if behind.** If there's no device in the room, drop it and say so in the submission.

## Off-code setup

- Physical Ledger device, up to date.
- Ledger **Key Ring CLI** installed; provision the operator key inside it and record the public address.
- Register that address as the operator on the `AgentWalletFactory` and on `RiskBudgetRegistry` (replacing the hot key from P5).

## Implementation

- **`api/agent_barbell/signers/signer.py`** — new abstract `Signer` with `get_address()` and `sign_transaction(tx)`. Same shape as `api/agent_hack/blockchain_data/blockchain_data_client.py`'s abstract-base-plus-implementations convention.
- **`api/agent_barbell/signers/local_signer.py`** — wraps the existing `eth_account` path from `TransactionManager`.
- **`api/agent_barbell/signers/ledger_key_ring_signer.py`** — shells out to the Key Ring CLI. Selected by `SIGNER=ledger`.
- **`api/agent_barbell/transaction_manager.py`** — take a `Signer` in the constructor instead of a raw private key. One-line change at every call site; do it with `lsp rename` rather than by hand.
- **`app/src/components/OperatorTrustPanel.tsx`** — copy `yieldseeker-app/app/src/components/AccountView.tsx` (128 lines). States plainly: who the operator is, that its key lives in hardware, and which actions (clearing the kill switch, withdrawing) only the human owner can ever take.
- **README.md** — add the trust-model section: LLM (proposes, bounded) / operator hardware key (executes within policy) / owner (withdraws, re-arms the kill switch). Judges on the Ledger, World and Privy tracks all read this.

**Done when:** a swap executes with the private key never present in the API process, provable by killing the Ledger connection and watching execution fail cleanly.

---

# Phase 8 — README, demo, submission
**T+21:00 → 24:00.** PR: `docs: submission and demo`

Goal: the prizes are decided here. A working product with a bad submission loses to a worse product with a good one.

## Off-code setup

- Record the demo video (2–4 min), following the `README.md` demo script exactly: policy from English → risk state from Substreams-derived history → **the hero moment** (shock → autonomous defence → on-chain `KillSwitchTriggered`) → security beat (raw transfer rejected at the contract level). Show the block explorer for every on-chain claim.
- Submit on ETHGlobal against every track: The Graph (both), Uniswap, Bazantic, Ledger. Each submission gets its own paragraph naming the exact file and tx hash that satisfies the brief — do not submit one generic blurb five times.
- Verify contracts on the Robinhood Chain explorer if you haven't.
- Have a fully funded, fully warmed demo account ready and a second one in reserve.

## Implementation

- **`README.md` — the only doc.** Restructure to lead with what the thing *is* and a screenshot, prize research below. Fold in: the trust model, the MCP tool schemas and client config, the verified 4663 addresses, and a short "merging back into yieldseeker" section naming what moves where (`RiskBudgetRegistry.sol` → `contracts/src/`; `risk_engine.py` → a new agent type under `agent_hack/`; `substreams/` as-is; the MCP service as a sibling of `xmtp-api/`). **No new markdown files** — one README, no `docs/` site, no scattered notes.
- **`plans/barbell-agent.md`** — the one exception, and only because it is written *for yieldseeker's repo, not ours*: the product doc in the exact house format of `yieldseeker-app/plans/agent-type-rebalancing.md` (title, `Status`, then `Idea` / `Why now` / `Mechanics` / `Risk` / `Competitive landscape` / `Fee design` / `Differentiation` / `Open questions`). It slots into their `plans/` directory as the next agent type and distinguishes us from the fixed-weight framing in their existing rebalancing doc.
- Final green pass across all four services, then tag.

**Done when:** video recorded, all tracks submitted with track-specific write-ups, and the live URLs work from a phone on venue wifi.

---

## Standing risks

- **Bridge latency (P0 step 2)** is the highest-variance item and blocks P1, P2 and P5. Start it in minute one.
- **Subgraph sync time (P3)** is a live-demo risk. Deploy from the P1 block, and build the api so it falls back to `RpcClient` if a Graph query is stale — the fallback must never be in the *reasoning* path, only the display path, or the Graph prize story weakens.
- **Robinhood Chain liquidity** on the chosen satellite may be thin enough that a real resize moves the price meaningfully. Size the demo wallet so slippage stays presentable, and set `minBuyAmount` honestly.
- **Hermes function-calling** is unproven. Gemini is the default. Don't spend hour 13 debugging a model.
- **Scope creep toward extra prizes.** World, ENS, Hedera, Arc and Circle all appear in the README's research. None of them are in this plan, deliberately. Five well-served tracks beat nine half-served ones, and every hour spent bolting on a chain we don't use is an hour stolen from P5.
