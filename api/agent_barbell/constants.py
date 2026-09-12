from __future__ import annotations

ROBINHOOD_CHAIN_ID = 4663

CHAIN_NAME_MAP: dict[int, str] = {
    ROBINHOOD_CHAIN_ID: 'Robinhood',
}

NATIVE_TOKEN_ADDRESS = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
MAX_UINT256 = 115792089237316195423570985008687907853269984665640564039457584007913129639935

AUTH_SIGNATURE_MAX_AGE_DAYS = 30
AUTH_SIGNATURE_ALLOWED_DOMAINS = {
    'agent-barbell.yieldseeker.xyz',
    # Local
    'localhost:3100',
    '127.0.0.1:3100',
    'localapp.kibalabs.xyz',
}

# NOTE: Robinhood Chain's stablecoin is USDG (Global Dollar, 6dp), not USDC — there is no
# canonical USDC deployment on 4663. Everything that would be USDC in yieldseeker is USDG here.
CHAIN_USDG_MAP: dict[int, str] = {
    ROBINHOOD_CHAIN_ID: '0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168',
}

CHAIN_WETH_MAP: dict[int, str] = {
    ROBINHOOD_CHAIN_ID: '0x0Bd7D308f8E1639FAb988df18A8011f41EAcAD73',
}

# The barbell's two legs. Anchor is the low-volatility safe leg, satellite is the
# high-volatility risk leg. Both are Robinhood Stock Tokens native to 4663.
CHAIN_ANCHOR_ASSET_MAP: dict[int, str] = {
    ROBINHOOD_CHAIN_ID: '0x92FD66527192E3e61d4DDd13322Aa222DE86F9B5',
}

CHAIN_SATELLITE_ASSET_MAP: dict[int, str] = {
    ROBINHOOD_CHAIN_ID: '0x1b0E319c6A659F002271B69dB8A7df2F911c153E',
}

CHAIN_SATELLITE_ASSET_OPTIONS_MAP: dict[int, tuple[str, ...]] = {
    ROBINHOOD_CHAIN_ID: (CHAIN_SATELLITE_ASSET_MAP[ROBINHOOD_CHAIN_ID],),
}

ASSET_SYMBOL_MAP: dict[str, str] = dict.fromkeys(CHAIN_USDG_MAP.values(), 'USDG') | dict.fromkeys(CHAIN_WETH_MAP.values(), 'WETH') | dict.fromkeys(CHAIN_ANCHOR_ASSET_MAP.values(), 'SGOV') | dict.fromkeys(CHAIN_SATELLITE_ASSET_MAP.values(), 'GME')
ASSET_NAME_MAP: dict[str, str] = {
    CHAIN_USDG_MAP[ROBINHOOD_CHAIN_ID]: 'Global Dollar',
    CHAIN_WETH_MAP[ROBINHOOD_CHAIN_ID]: 'Wrapped Ether',
    CHAIN_ANCHOR_ASSET_MAP[ROBINHOOD_CHAIN_ID]: 'Short-term treasury ETF token',
    CHAIN_SATELLITE_ASSET_MAP[ROBINHOOD_CHAIN_ID]: 'GameStop',
}
ASSET_DECIMALS_MAP: dict[str, int] = dict.fromkeys(CHAIN_USDG_MAP.values(), 6) | dict.fromkeys(CHAIN_WETH_MAP.values(), 18) | dict.fromkeys(CHAIN_ANCHOR_ASSET_MAP.values(), 18) | dict.fromkeys(CHAIN_SATELLITE_ASSET_MAP.values(), 18)

SUPPORTED_BASE_ASSETS: dict[int, set[str]] = {
    ROBINHOOD_CHAIN_ID: {
        CHAIN_USDG_MAP[ROBINHOOD_CHAIN_ID],
        CHAIN_ANCHOR_ASSET_MAP[ROBINHOOD_CHAIN_ID],
        *CHAIN_SATELLITE_ASSET_OPTIONS_MAP[ROBINHOOD_CHAIN_ID],
    },
}

UNISWAP_V3_ROUTER_ADDRESS_MAP: dict[int, str] = {
    ROBINHOOD_CHAIN_ID: '0xCaf681a66D020601342297493863E78C959E5cb2',
}

UNISWAP_V3_FACTORY_ADDRESS_MAP: dict[int, str] = {
    ROBINHOOD_CHAIN_ID: '0x1f7d7550B1b028f7571E69A784071F0205FD2EfA',
}

MULTICALL3_ADDRESS_MAP: dict[int, str] = {
    ROBINHOOD_CHAIN_ID: '0xcA11bde05977b3631167028862bE2a173976CA11',
}

# Uniswap V3 fee tier (in hundredths of a bip) for each leg's pool against USDG. These are
# the deepest pools on 4663 as of deployment; AWKUniswapV3SwapAdapter rejects any tier
# outside {100, 500, 3000, 10000}.
ANCHOR_POOL_FEE = 3000
SATELLITE_POOL_FEE = 10000

ANCHOR_POOL_ADDRESS_MAP: dict[int, str] = {
    ROBINHOOD_CHAIN_ID: '0xfAb520051f96F4D2a32c22B6a3dD7fFfdf231bFe',
}

SATELLITE_POOL_ADDRESS_MAP: dict[int, str] = {
    ROBINHOOD_CHAIN_ID: '0xE9713f453aDB9245B19559790c96F470a18F2fDF',
}

MAX_BPS = 10000

AGENT_CHAT_MAX_STEPS = 8

ROBINHOOD_BLOCK_TIME_SECONDS = 0.1

BARBELL_NAME_MIN_LENGTH = 3
BARBELL_NAME_MAX_LENGTH = 30
BARBELL_NAME_ALLOWED_CHARACTERS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ._&$-'")

# Risk engine defaults. Every one of these is a bound the deterministic engine enforces;
# the language model can move a policy within these bounds but never outside them.
DEFAULT_MAX_DRAWDOWN_BPS = 1500
DEFAULT_TARGET_SATELLITE_BPS = 2000
DEFAULT_MAX_SATELLITE_BPS = 4000
MIN_MAX_DRAWDOWN_BPS = 300
MAX_MAX_DRAWDOWN_BPS = 5000
REBALANCE_BAND_BPS = 300
VOLATILITY_WINDOW_DAYS = 14
MOMENTUM_WINDOW_DAYS = 7
TARGET_PORTFOLIO_VOLATILITY = 0.20

DAYS_PER_YEAR = 365
SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60
SECONDS_PER_HOUR = 60 * 60

# Populated by contracts/deployments.json once Phase 1 deploys. Keys must match the
# deployments.json key names so the two can be diffed by eye.
AB_DEPLOYMENTS_MAP: dict[int, dict[str, str]] = {
    4663: {
        'adapterRegistry': '0x2e3023BFe3128Bbb3e51426475EF69CDAD76e199',
        'agentWalletFactory': '0x0c86984CD94736de2989d7700BbE00eec3F01ef1',
        'agentWalletImplementation': '0xB593dF9ba21584d3db3d897DCa004C2cEe12307F',
        'riskBudgetRegistry': '0x2AC766FcC38e0e9Faa280bdFf91D49a006b040aC',
        'sellPolicy': '0xCF309CB284A6b12B8A060D70f80f19f1F8A076C5',
        'uniswapV3SwapAdapter': '0x2c5Fc263eeF5D5b3C2dEa4598E0C3e32EcF91AaC',
    }
}
AB_ADAPTER_REGISTRY_ADDRESS_MAP = {chainId: deployments['adapterRegistry'] for chainId, deployments in AB_DEPLOYMENTS_MAP.items()}
AB_AGENT_WALLET_FACTORY_ADDRESS_MAP = {chainId: deployments['agentWalletFactory'] for chainId, deployments in AB_DEPLOYMENTS_MAP.items()}
AB_AGENT_WALLET_IMPLEMENTATION_ADDRESS_MAP = {chainId: deployments['agentWalletImplementation'] for chainId, deployments in AB_DEPLOYMENTS_MAP.items()}
AB_RISK_BUDGET_REGISTRY_ADDRESS_MAP = {chainId: deployments['riskBudgetRegistry'] for chainId, deployments in AB_DEPLOYMENTS_MAP.items()}
AB_SELL_POLICY_ADDRESS_MAP = {chainId: deployments['sellPolicy'] for chainId, deployments in AB_DEPLOYMENTS_MAP.items()}
AB_UNISWAP_V3_SWAP_ADAPTER_ADDRESS_MAP = {chainId: deployments['uniswapV3SwapAdapter'] for chainId, deployments in AB_DEPLOYMENTS_MAP.items()}
