# mypy: disable-error-code="typeddict-unknown-key, misc, list-item, typeddict-item"

from eth_typing import ABI

ERC20_ABI: ABI = [
    {'inputs': [], 'name': 'name', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'symbol', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'decimals', 'outputs': [{'internalType': 'uint8', 'name': '', 'type': 'uint8'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'totalSupply', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [{'internalType': 'address', 'name': 'account', 'type': 'address'}], 'name': 'balanceOf', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'},
    {
        'inputs': [{'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}],
        'name': 'transfer',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
]

UNISWAP_V3_ROUTER_ABI: ABI = [
    {'inputs': [], 'name': 'factory', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'WETH9', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'},
]

UNISWAP_V3_FACTORY_ABI: ABI = [
    {
        'inputs': [{'internalType': 'address', 'name': 'tokenA', 'type': 'address'}, {'internalType': 'address', 'name': 'tokenB', 'type': 'address'}, {'internalType': 'uint24', 'name': 'fee', 'type': 'uint24'}],
        'name': 'getPool',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'stateMutability': 'view',
        'type': 'function',
    },
]

UNISWAP_V3_POOL_ABI: ABI = [
    {'inputs': [], 'name': 'liquidity', 'outputs': [{'internalType': 'uint128', 'name': '', 'type': 'uint128'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'token0', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'token1', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'fee', 'outputs': [{'internalType': 'uint24', 'name': '', 'type': 'uint24'}], 'stateMutability': 'view', 'type': 'function'},
    {
        'inputs': [],
        'name': 'slot0',
        'outputs': [
            {'internalType': 'uint160', 'name': 'sqrtPriceX96', 'type': 'uint160'},
            {'internalType': 'int24', 'name': 'tick', 'type': 'int24'},
            {'internalType': 'uint16', 'name': 'observationIndex', 'type': 'uint16'},
            {'internalType': 'uint16', 'name': 'observationCardinality', 'type': 'uint16'},
            {'internalType': 'uint16', 'name': 'observationCardinalityNext', 'type': 'uint16'},
            {'internalType': 'uint8', 'name': 'feeProtocol', 'type': 'uint8'},
            {'internalType': 'bool', 'name': 'unlocked', 'type': 'bool'},
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
]

AGENT_WALLET_FACTORY_ABI: ABI = [
    {
        'inputs': [{'internalType': 'address', 'name': 'owner', 'type': 'address'}, {'internalType': 'uint256', 'name': 'ownerAgentIndex', 'type': 'uint256'}],
        'name': 'createAgentWallet',
        'outputs': [{'internalType': 'address', 'name': 'ret', 'type': 'address'}],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'address', 'name': 'owner', 'type': 'address'}, {'internalType': 'uint256', 'name': 'ownerAgentIndex', 'type': 'uint256'}],
        'name': 'getAddress',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {'inputs': [], 'name': 'adapterRegistry', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'agentWalletImplementation', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'},
]

AGENT_WALLET_ABI: ABI = [
    {'inputs': [], 'name': 'owner', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'},
    {
        'inputs': [
            {'internalType': 'address', 'name': 'adapter', 'type': 'address'},
            {'internalType': 'address', 'name': 'target', 'type': 'address'},
            {'internalType': 'bytes', 'name': 'data', 'type': 'bytes'},
        ],
        'name': 'executeViaAdapter',
        'outputs': [{'internalType': 'bytes', 'name': '', 'type': 'bytes'}],
        'stateMutability': 'payable',
        'type': 'function',
    },
]

ADAPTER_REGISTRY_ABI: ABI = [
    {'inputs': [], 'name': 'getAllTargets', 'outputs': [{'internalType': 'address[]', 'name': '', 'type': 'address[]'}], 'stateMutability': 'view', 'type': 'function'},
    {
        'inputs': [{'internalType': 'address', 'name': 'target', 'type': 'address'}],
        'name': 'getTargetAdapter',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'stateMutability': 'view',
        'type': 'function',
    },
]

RISK_BUDGET_REGISTRY_ABI: ABI = [
    {
        'inputs': [{'internalType': 'address', 'name': 'wallet', 'type': 'address'}],
        'name': 'getPolicy',
        'outputs': [
            {
                'components': [
                    {'internalType': 'uint16', 'name': 'maxDrawdownBps', 'type': 'uint16'},
                    {'internalType': 'uint16', 'name': 'targetSatelliteBps', 'type': 'uint16'},
                    {'internalType': 'uint16', 'name': 'maxSatelliteBps', 'type': 'uint16'},
                    {'internalType': 'uint64', 'name': 'updatedAt', 'type': 'uint64'},
                    {'internalType': 'bool', 'name': 'isKilled', 'type': 'bool'},
                ],
                'internalType': 'struct RiskBudgetRegistry.Policy',
                'name': '',
                'type': 'tuple',
            }
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'address', 'name': 'wallet', 'type': 'address'}],
        'name': 'isKilled',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [
            {'internalType': 'address', 'name': 'wallet', 'type': 'address'},
            {
                'components': [
                    {'internalType': 'uint16', 'name': 'maxDrawdownBps', 'type': 'uint16'},
                    {'internalType': 'uint16', 'name': 'targetSatelliteBps', 'type': 'uint16'},
                    {'internalType': 'uint16', 'name': 'maxSatelliteBps', 'type': 'uint16'},
                    {'internalType': 'uint64', 'name': 'updatedAt', 'type': 'uint64'},
                    {'internalType': 'bool', 'name': 'isKilled', 'type': 'bool'},
                ],
                'internalType': 'struct RiskBudgetRegistry.Policy',
                'name': 'policy',
                'type': 'tuple',
            },
        ],
        'name': 'setPolicy',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [
            {'internalType': 'address', 'name': 'wallet', 'type': 'address'},
            {'internalType': 'uint16', 'name': 'drawdownBps', 'type': 'uint16'},
            {'internalType': 'uint16', 'name': 'newSatelliteBps', 'type': 'uint16'},
            {'internalType': 'string', 'name': 'reason', 'type': 'string'},
        ],
        'name': 'recordKillSwitch',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
]
