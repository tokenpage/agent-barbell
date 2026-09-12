# ETHOnline 2026 — Hackathon Plan

Event: https://ethglobal.com/events/ethonline2026/prizes/ (11 sponsor prize pools, $80k total). No separate "best overall ETHGlobal" cash prize found on the prizes page — check the event's finalists/main page closer to submission in case a pool prize appears there.

Two submission tracks per most sponsors:
- **Net-new / "Start Fresh"** — built during the event.
- **Continuity** — extends an existing repo/product (e.g. YieldSeeker, AgentWalletKit) with pre-existing work documented and only new work judged.

We qualify for Continuity on anything that extends AgentWalletKit or YieldSeeker itself — worth defaulting to since it doubles our eligible pool per sponsor and matches "planned new agent type" work we'd do anyway.

## Prize categories

| Sponsor | Total | What they want | Continuity-only slice | Net-new-only slice |
|---|---|---|---|---|
| **The Graph** | $15,000 | (1) Compose 2+ Graph products or extend a Standardized Subgraph — $5k. (2) AI tooling/agents using Subgraphs/Substreams/MCP as live data source — $5k **From Scratch** pool + $5k **Continuity** pool (same brief, judged separately) | AI track continuity pool, $5k | Composable/Standardized track + AI From Scratch pool, $10k |
| **Hedera** | $15,000 | (1) Live x402-gated service on Hedera (Blocky402) + consuming agent — $6k, up to 3 teams. (2) Improve/port the Hedera dev harness — $2k. (3) Tokenize a real asset class via Asset Tokenization Studio (ERC-3643/1400, compliance, lifecycle) — $6k, up to 3 teams. (4) Bring back a prior Hedera project with substantive new work — $1k | Continuity track, $1k | Everything else nominally open to both, but "started fresh" framing dominates |
| **Arc (Circle)** | $10,000 | Stablecoin-native DeFi (lending/FX/treasury) on Arc+USDC — $1,667. Agentic economy app on Circle Agent Stack (agent wallets, USDC payments, Nanopayments) — $1,667. Same two briefs combined, continuity-only — $1,666. Ship a working Arc integration in a project that's mainnet-ready by Sept 30 — $3,500 net-new / $1,500 continuity | $1,666 (combined) + $1,500 (mainnet-ready) = $3,166 | $1,667 + $1,667 + $3,500 = $6,834 |
| **World** | $7,000 | AgentKit: distinguish a human-backed agent from a bot for access/commerce/trust — $3,500, **continuity only**. Selfie Check: low-friction biometric signal for risk/eligibility/fairness/abuse-prevention — $3,500, open track | $3,500 (AgentKit) | $3,500 (Selfie Check, but open to either track) |
| **1inch** | $7,000 | Build a custom Aqua app (self-custodial LP positions) on SwapVM opcodes — $5k net-new, $2k continuity | $2,000 | $5,000 |
| **ENS** | $5,000 | Best use of ENSv2 (hierarchical registries, Enhanced Access Control, Permissioned Resolvers, subname aliasing) — $4,500 open. Integrate ENSv2 into an *existing* project — $500, continuity only. Bonus interest in AI-agent identity/namespaces | $500 (+ ENSv2 track open to us too) | $4,500 |
| **Uniswap Foundation** | $5,000 | Build on/integrate any Uniswap stack piece (v2/v3/v4, hooks, API, CCA) — $3k net-new, $2k continuity | $2,000 | $3,000 |
| **Ledger** | $5,000 | AI agents/products using Ledger as trust layer — hardware-backed secrets an agent can't leak (Key Ring CLI), agent payments, human-in-the-loop approval for high-risk actions — $3,500 net-new, $1,500 continuity (add a Ledger signer/Key Ring to something you already shipped) | $1,500 | $3,500 |
| **Privy** | $5,000 | Best B2B financial product (treasury, org wallets, policies, quorum approvals) — $2,500. Best financial flow (funding/moving/spending assets, hides onchain complexity) — $2,500. No explicit continuity split | — | — (open track both) |
| **Chainlink** | $3,000 | CRE Confidential Workflows (TEE-executed, secrets/private thresholds never leave enclave) — $2k, up to 2 teams. Chainlink-powered upgrade to an *existing* project (Price Feeds/Data Streams/PoR/VRF/CRE, must hit onchain state) — $500, continuity only. Automated Liquidation Protection Challenge — $500, join via Sepolia contract, judged by simulated market scenarios | $500 (upgrade track) | — |
| **Bazantic** | $3,000 | Help an agent use *your* hackathon project via Bazantic MCP + "Recipe," prove before/after improvement — $1k, **continuity only**, up to 2 teams. Best recipe chaining 2+ sponsor APIs — $1k. Bring a brand-new API into Bazantic + build a recipe — $1k | $1,000 | $2,000 |

Notable cross-cutting angles for us specifically:
- **AgentWalletKit is our own open-source infra** (contracts + landing page already shipped) → any prize that rewards "AI tooling that makes X easier to use from AI environments" (Graph AI track, Bazantic, Hedera x402) is a natural continuity fit: wrap AgentWalletKit itself as MCP/skill/recipe tooling, not just a one-off app.
- **Ledger + World AgentKit + ENS** all reward "prove a human or a hardware key is behind this agent's high-risk actions" — directly matches AgentWalletKit's non-custodial, scoped-authority design philosophy (owner-controlled withdrawal, no unrestricted arbitrary-call path).
- **Chainlink CRE Confidential Workflows + Automated Liquidation Protection Challenge** map almost 1:1 onto our own Borrowing/Basis Trade Agent research (liquidation monitoring, private risk thresholds).
- **Hedera Tokenization of Anything (ATS)** and **Arc stablecoin DeFi** map onto our tokenized-stock research (Coinbase B20 on Base, Robinhood Chain on Arbitrum) even though neither sponsor chain is one we currently deploy to — would require a scoped new integration, not a port of existing YieldSeeker contracts.

## Ideas

Kept high-level — pick one to scope in detail before building.

### 1. Chat-native AgentWalletKit copilot (Grok/Hermes direct integration)
Wrap AgentWalletKit as an MCP server + reusable "recipe"/skill so an external chat agent (xAI Grok API, or a Hermes/Nous model via OpenRouter) can directly query a wallet's positions and propose/execute scoped operations through the existing adapter-registry guardrails — no custom frontend required, the agent *is* the interface.
- Hits: Bazantic "Help an agent use your hackathon project" (continuity, we already have the project), Bazantic recipe/new-API prizes, The Graph AI tooling track (if positions/history are served via a Subgraph), Hedera x402 track (meter the copilot's calls per-query).
- Natural continuity story: AgentWalletKit already ships, MCP/recipe layer is genuinely new work.

### 2. Confidential risk & liquidation copilot (Chainlink CRE + Ledger)
Productize the Borrowing/Basis Trade Agent research: an agent that watches collateral health / funding rate / basis risk and holds the user's private risk thresholds and protective-action rules *inside a TEE* (Chainlink CRE Confidential Workflow), with the underlying signer secured by a Ledger Key Ring instead of a hot key.
- Hits: Chainlink Confidential Workflow ($2k) + Automated Liquidation Protection Challenge ($500, direct simulated judging) + Ledger AI Agents ($3.5k, "human-in-the-loop agent that approves high-risk actions before funds move").
- Strongest fit to "risk analysis" + "privacy" + "security" zeitgeist items; reuses agent-type-borrowing.md and agent-type-basistrade.md research almost directly.

### 3. Risk-budget barbell agent (Robinhood Chain only)
Not a target-weight rebalancer — the user states a **loss budget**, not a portfolio. The agent runs a barbell entirely on Robinhood Chain: a stable tokenized-blue-chip anchor (NVDA/AAPL-style) + a volatile meme/RWA satellite, both native to that chain's own tokenized-stock catalog — no bridging or cross-chain coordination needed. Dynamically resizes the satellite via volatility targeting, a momentum overlay, and a hard drawdown kill-switch — meme-stock upside without needing to babysit or panic-sell it. Distinct from the existing Rebalancing Agent doc's fixed-weight framing, and from what Glider/Bitwise ship today (fixed model weights, no risk-budget concept).
- Hits: Uniswap (swap execution on Robinhood Chain's own Uniswap deployment), Chainlink + Ledger (the kill-switch is exactly "confidential private thresholds" + "human/hardware approval before a high-risk defensive action"), zeitgeist alignment (tokenized stocks + Robinhood chain meme stocks + risk analysis, explicitly).
- **Fresh deployment, not an extension of our live Base infra.** A wholly new AgentWalletKit instance (factory/registry/adapters) deployed on Robinhood Chain only — no shared state or addresses with our production Base contracts.

### 4. ENS identity & reputation layer for agents — deferred
Give every agent an ENSv2 subname under a permissioned registry, recording strategy, risk parameters, and track record as text records — a discoverable identity layer other agents/users can query before trusting an agent.
- **Deferred for this build.** ENSv2 is Sepolia-only today; we don't want testnet-only pieces in the demo. Revisit once ENSv2 is on mainnet, or if a later cut of the product specifically needs third-party/agent-to-agent discovery (e.g. a Bazantic-style marketplace where other agents need to look us up before paying us).

### 5. Metered risk-scoring API for agents (x402)
Expose YieldSeeker's existing vault risk-scoring / fee-decoding engine as a pay-per-call x402-gated service (Hedera + Blocky402, or Circle Nanopayments on Arc), so third-party agents can pay-per-query instead of needing an API key.
- Hits: Hedera AI & Agentic Payments ($6k pool), Bazantic "Agentify a new API" ($1k), Arc Agentic Economy track.
- Smallest scope of the five — productizes something we already compute internally; main new work is the payment-gated service wrapper and a demo consumer agent.

## Recommended build: Barbell Agent — merged 1 + 3 (+ risk-defense from 2), context assembled via The Graph

Single chain, single fresh deployment: everything runs on Robinhood Chain mainnet only. A wholly new AgentWalletKit instance (factory, registry, adapters) deployed specifically for this project — no dependency on, or shared state with, our live Base contracts. Robinhood Chain hosts both legs of the barbell natively (tokenized blue-chip stocks and meme/RWA tokens both trade there), so the barbell doesn't need bridging or cross-chain coordination to exist. Not a rebalancer: the user hands the agent a **risk budget** ("never lose more than 15% from peak"), not a spreadsheet of percentages, and the agent's whole job is defending that number while capturing meme-stock/tokenized-equity upside. The Graph is the context layer this reasoning runs on: instead of hand-assembling state from raw RPC calls, the agent fires structured queries against indexed Subgraphs and gets the volatility/momentum/drawdown inputs it needs in one shot.

**Why it's feasible, not just ambitious:**
- Robinhood Chain is live mainnet (chain ID 4663) since Jul 1 2026: EVM-compatible Arbitrum Orbit, Uniswap is the dominant DEX there ($1.89B/day volume), tokenized stocks (NVDA/AAPL-style) are a significant share of that volume, memecoins and tokenized stocks trade side by side, contract deployment is permissionless.
- `contracts/src/adapters/UniswapV3SwapAdapter.sol` (wrapping the generic `AWKUniswapV3SwapAdapter`) already exists as proven, tested code — deployed on Base today, keyed by `chainId` in `Deploy.s.sol`. Standing it up fresh on Robinhood Chain is pointing the same deploy script at a new router address, not new Solidity.
- **Robinhood Chain Mainnet has first-class, documented support in Subgraph Studio today** (thegraph.com/docs/en/supported-networks/robinhood/) — not a workaround, a fully supported network.

**Architecture:**
1. **Contracts** — deploy a fresh AgentWalletKit factory/registry/`UniswapV3SwapAdapter` on Robinhood Chain via the existing `Deploy.s.sol` script pattern, targeting only that chain. Add one small new `RiskBudgetRegistry` contract, also fresh on Robinhood Chain, whose only job is to emit a `PolicyUpdated` event when the user's risk budget/barbell policy changes, and a `KillSwitchTriggered` event when the drawdown circuit-breaker fires — gives the Subgraph something to index and a public, verifiable on-chain trail ("what did the agent promise, and did it actually defend it") without needing ENS (deferred) for that role.
2. **Context layer (The Graph)** — one Subgraph on Robinhood Chain indexing wallet balances, `PolicyUpdated`/`KillSwitchTriggered` history, adapter-executed swaps, and enough price-tick history to derive realized volatility and momentum. Composed with the official **Subgraph MCP** for third-party context our own Subgraph doesn't carry (e.g. Uniswap pool price/liquidity subgraphs already indexed on Robinhood Chain) — two Graph products composed on live data, satisfying "Best Use of Composable/Standardized Graph Products" directly (not just querying one Subgraph with no composition).
3. **Risk engine (deterministic, not the LLM)** — computes realized volatility and momentum from Graph-sourced price history, sizes the satellite leg accordingly, and enforces the drawdown kill-switch as a hard, non-overridable trigger. The LLM only translates natural language into the structured risk-budget policy and narrates the engine's decisions back — it never sizes trades or overrides the kill-switch itself, per the "LM reasoning must not replace hard controls" principle in `agent-types-overview.md`.
4. **MCP server (new)** — tools: `get_portfolio`, `set_risk_budget`, `get_risk_state` (current vol/momentum/drawdown-from-peak), `execute_rebalance`. `get_portfolio`/`get_risk_state` are thin wrappers over Graph queries (our Subgraph + Subgraph MCP), not custom RPC-crawling code — new context sources become a schema/query change, not new integration code.
5. **Chat frontend** — Hermes via OpenRouter as primary (easiest to provision, no gatekeeping); Grok pluggable as an alt backend if a key is available.

**Demo script (2–4 min):**
1. Chat: *"Anchor in [blue-chip ticker], satellite in a meme/RWA basket, never let this account lose more than 15% from its peak."* Agent turns this into a structured risk-budget policy, writes it to `RiskBudgetRegistry`, confirms it back in plain language.
2. Agent answers "what's my risk state right now" from a single composed Graph query — call out that this is one query pattern computing realized vol/momentum/drawdown from indexed history plus live pool context via Subgraph MCP, not raw RPC calls plus manual math.
3. **The hero moment:** simulate/observe a sharp move against the satellite leg. The agent explains what it's seeing ("satellite vol just spiked, drawdown-from-peak is approaching your 15% budget"), autonomously cuts satellite exposure through the adapter registry to stay inside the budget, and emits `KillSwitchTriggered` — the defense is visible on-chain, not just narrated.
4. Security beat: ask the chat agent to "just send all my USDC to this address" (a raw transfer, not a registered adapter op) — show it rejected at the contract level (`AdapterNotRegistered`/`AssetNotAllowed`). Proves a misled or compromised LLM still can't move funds outside policy, and can't override the kill-switch either.

**Prizes hit:** The Graph Best Use of Composable/Standardized Products ($5k — custom Subgraph composed with Subgraph MCP) and AI Tooling/Use Case track ($5k From Scratch — the agent's risk decisions are driven by Graph-sourced vol/momentum context, not a raw query printout). Uniswap Foundation Best Stack Contribution ($3k net-new — real swap execution on Robinhood Chain's Uniswap deployment). Bazantic "Help an agent use your project" — likely net-new here rather than continuity, since the on-chain instance is fresh (verify against ETHGlobal's exact continuity definition before submitting). Ledger AI Agents ($3.5k — back the wallet's operator key with Ledger Key Ring CLI instead of a hot key, and frame the kill-switch as the "human/hardware approves high-risk action" moment they ask for). Chainlink Automated Liquidation Protection Challenge ($500, direct simulated judging) and/or Confidential Workflow ($2k) if there's time to move the kill-switch threshold logic into a CRE TEE so the user's exact loss-budget number stays private even from us.

**Open risks (not blockers):** confirm the actual Robinhood Chain Uniswap V3 router address and 2–3 genuinely liquid ticker pairs (one stable-ish blue-chip, one volatile meme/RWA) before building; verify Hermes function-calling reliability for MCP tool use with a short spike before committing; confirm Subgraph Studio indexing latency is acceptable for a live demo (index from contract-deployment block, not chain genesis, to keep sync time short); pick the simplest realized-volatility/momentum formula that's still demo-legible (e.g. rolling stdev of indexed price ticks) rather than anything requiring a model; since this is a fresh, standalone deployment rather than an extension of live Base infra, double-check whether ETHGlobal counts reusing AgentWalletKit's open-source *contract code* (not its live state) as Continuity, or whether this submission is cleaner as Net-new.

## Development

Two services: `api/` (Starlette + kiba-core + SQLAlchemy/Alembic, Python/uv) and `app/` (React via kibalabs-build/Vite). See `implementation-plan.md` for the phased build plan.

### Local setup

```bash
# api
cd api && make install

# app
cd app && make install
```

`api/` needs a PostgreSQL instance reachable via the `DB_*` env vars. `db-setup.sql` provisions an isolated `barbelldb` database and `barbell_admin` login on the shared RDS instance. Barbell uses `barbelldb`'s `public` schema, matching YieldSeeker. Run it once with the existing `yieldseeker_admin` Terraform admin from a host that can reach the private RDS network. It prompts for the new `barbell_admin` password; no password is stored in this repo.

```bash
psql --host="$REMOTE_DB_HOST" --port="$REMOTE_DB_PORT" \
  --username="$REMOTE_DB_USERNAME" --dbname="$REMOTE_DB_NAME" \
  --file=db-setup.sql
```

After the bootstrap, use `DB_NAME=barbelldb`, `DB_USERNAME=barbell_admin`, and the password entered by the script when running Alembic:

```bash
cd api
DB_HOST=... DB_PORT=5432 DB_NAME=barbelldb DB_USERNAME=barbell_admin DB_PASSWORD=... uv run --active alembic upgrade head
```

### Running locally

```bash
# api — http://127.0.0.1:5100
cd api && DB_HOST=... DB_PORT=... DB_NAME=... DB_USERNAME=... DB_PASSWORD=... make start

# app — http://127.0.0.1:3100
cd app && make start
```

Or both together via `docker-compose up` from the repo root (the api container still needs the `DB_*` env vars set, e.g. via a local `.env` file passed to `docker compose`).

### Checks

```bash
cd api && make lint-check && make type-check
cd app && npx lint && npx type-check
```

### Deployment

Same mechanism `yieldseeker-app` uses, on the same shared infra — not Fly.io, not a separate AWS account.

- **`api`** deploys as a `docker run` container on the shared appbox EC2 instance, discovered by its `nginx-proxy` via `VIRTUAL_HOST` (`.github/workflows/api-deploy.yml`, mirrors `yieldseeker-app/.github/workflows/api-deploy.yml`). Domain: `agent-barbell-api.yieldseeker.xyz`.
- **`app`** builds statically and syncs to the same S3 bucket + CloudFront distribution as `yieldseeker-app`, under a new path prefix (`.github/workflows/app-deploy.yml`, mirrors `yieldseeker-app/.github/workflows/app-deploy.yml`). Domain: `agent-barbell.yieldseeker.xyz`.

**Not yet actually deployed** — this repo needs its own copy of the relevant GitHub Actions secrets (`YS_APPBOX_URL`, `YS_APPBOX_USER`, `YS_APPBOX_SSH_KEY`, `YS_APPBOX_PORT` for the api; `SITE_DEPLOYER_AWS_ACCESS_KEY_ID`, `SITE_DEPLOYER_AWS_SECRET_ACCESS_KEY`, `SITE_DEPLOYER_AWS_REGION`, `SITE_DEPLOYMENT_S3_BUCKET_NAME`, `SITE_DEPLOYMENT_CLOUDFRONT_ID` for the app — same values `yieldseeker-app` uses, since it's the same box/bucket/distribution), plus DNS: an A record for `agent-barbell-api.yieldseeker.xyz` pointing at the appbox EIP, and a CNAME/alias for `agent-barbell.yieldseeker.xyz` pointing at the CloudFront distribution (added as an alternate domain name on that distribution first). None of that is set up yet.

The api container also needs a `~/.agent-barbell-api.vars` env file on the appbox (same pattern as `~/.yieldseeker-api.vars`) containing `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`, `AUTH_ALLOWED_DOMAINS`.

`.github/workflows/api-check.yml` and `app-check.yml` run lint/type-check/security-check on every PR touching their respective directories.
