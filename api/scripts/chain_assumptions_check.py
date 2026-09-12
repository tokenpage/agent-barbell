# ruff: noqa: T201
"""Re-verify every hardcoded Robinhood Chain assumption against live mainnet.

Run after any change to constants.py, and before the demo:
    cd api && direnv exec . uv run --active python scripts/chain_assumptions_check.py
"""

import asyncio

from core.requester import Requester
from core.util import chain_util
from core.web3.eth_client import ContractCall

import _path_fix  # type: ignore[import-not-found]  # noqa: F401
from agent_barbell import constants
from agent_barbell.barbell_abis import ERC20_ABI
from agent_barbell.barbell_abis import UNISWAP_V3_FACTORY_ABI
from agent_barbell.barbell_abis import UNISWAP_V3_POOL_ABI
from agent_barbell.barbell_abis import UNISWAP_V3_ROUTER_ABI
from agent_barbell.create_system_manager import create_system_manager
from agent_barbell.create_system_manager import use_system_manager
from agent_barbell.system_manager import SystemManager

CHAIN_ID = constants.ROBINHOOD_CHAIN_ID
MIN_ACCEPTABLE_POOL_DEPTH_USD = 100_000


def _check(description: str, actual: object, expected: object) -> bool:
    isOk = str(actual).lower() == str(expected).lower()
    print(f'{"PASS" if isOk else "FAIL"}  {description}')
    if not isOk:
        print(f'        expected: {expected}')
        print(f'        actual:   {actual}')
    return isOk


async def do_stuff(systemManager: SystemManager) -> None:
    ethClient = systemManager.ethClientManager.get_regular_client(chainId=CHAIN_ID)
    routerAddress = constants.UNISWAP_V3_ROUTER_ADDRESS_MAP[CHAIN_ID]
    factoryAddress = constants.UNISWAP_V3_FACTORY_ADDRESS_MAP[CHAIN_ID]
    anchorAddress = constants.CHAIN_ANCHOR_ASSET_MAP[CHAIN_ID]
    satelliteAddress = constants.CHAIN_SATELLITE_ASSET_MAP[CHAIN_ID]
    usdgAddress = constants.CHAIN_USDG_MAP[CHAIN_ID]
    results: list[bool] = []

    print('=== chain ===')
    chainId = await ethClient.get_latest_block_number()
    print(f'      latest block: {chainId}')

    print('=== uniswap ===')
    routerFactory, routerWeth = await ethClient.multicall(
        [
            ContractCall(toAddress=routerAddress, contractAbi=UNISWAP_V3_ROUTER_ABI, functionName='factory', arguments={}),
            ContractCall(toAddress=routerAddress, contractAbi=UNISWAP_V3_ROUTER_ABI, functionName='WETH9', arguments={}),
        ],
        shouldUseMulticall3=True,
    )
    results.append(_check('router.factory() matches configured factory', chain_util.normalize_address(routerFactory[0]), factoryAddress))
    results.append(_check('router.WETH9() matches configured WETH', chain_util.normalize_address(routerWeth[0]), constants.CHAIN_WETH_MAP[CHAIN_ID]))

    print('=== assets ===')
    for address, expectedSymbol in ((anchorAddress, 'SGOV'), (satelliteAddress, 'GME'), (usdgAddress, 'USDG')):
        symbolResponse, decimalsResponse = await ethClient.multicall(
            [
                ContractCall(toAddress=address, contractAbi=ERC20_ABI, functionName='symbol', arguments={}),
                ContractCall(toAddress=address, contractAbi=ERC20_ABI, functionName='decimals', arguments={}),
            ],
            shouldUseMulticall3=True,
        )
        results.append(_check(f'{address} symbol', symbolResponse[0], expectedSymbol))
        results.append(_check(f'{expectedSymbol} decimals', decimalsResponse[0], constants.ASSET_DECIMALS_MAP[address]))

    print('=== pools ===')
    for legName, legAddress, legFee in (('anchor', anchorAddress, constants.ANCHOR_POOL_FEE), ('satellite', satelliteAddress, constants.SATELLITE_POOL_FEE)):
        poolResponse = await ethClient.call_function_by_name(
            toAddress=factoryAddress,
            contractAbi=UNISWAP_V3_FACTORY_ABI,
            functionName='getPool',
            arguments={'tokenA': legAddress, 'tokenB': usdgAddress, 'fee': legFee},
        )
        poolAddress = chain_util.normalize_address(poolResponse[0])
        if poolAddress == chain_util.normalize_address('0x0000000000000000000000000000000000000000'):
            print(f'FAIL  {legName} pool at fee {legFee} does not exist')
            results.append(False)
            continue
        liquidityResponse, usdgBalanceResponse = await ethClient.multicall(
            [
                ContractCall(toAddress=poolAddress, contractAbi=UNISWAP_V3_POOL_ABI, functionName='liquidity', arguments={}),
                ContractCall(toAddress=usdgAddress, contractAbi=ERC20_ABI, functionName='balanceOf', arguments={'account': poolAddress}),
            ],
            shouldUseMulticall3=True,
        )
        usdgDepth = int(usdgBalanceResponse[0]) / (10 ** constants.ASSET_DECIMALS_MAP[usdgAddress])
        hasDepth = usdgDepth > MIN_ACCEPTABLE_POOL_DEPTH_USD
        print(f'{"PASS" if hasDepth else "FAIL"}  {legName} pool {poolAddress} fee={legFee} usdgDepth=${usdgDepth:,.0f} liquidity={int(liquidityResponse[0])}')
        results.append(hasDepth)

    print('=== deployments ===')
    if not constants.AB_DEPLOYMENTS_MAP:
        print('SKIP  AB_DEPLOYMENTS_MAP is empty — contracts not deployed yet')
    else:
        for name, address in constants.AB_DEPLOYMENTS_MAP[CHAIN_ID].items():
            code = await ethClient.get_code(address=address)
            hasCode = len(code) > 2  # noqa: PLR2004
            print(f'{"PASS" if hasCode else "FAIL"}  {name} has code at {address}')
            results.append(hasCode)

    print()
    print(f'{sum(results)}/{len(results)} checks passed')


async def main() -> None:
    systemManager = create_system_manager()
    async with use_system_manager(systemManager=systemManager):
        await do_stuff(systemManager=systemManager)


if __name__ == '__main__':
    asyncio.run(main())
    asyncio.run(Requester().close_connections())
