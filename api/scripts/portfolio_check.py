# ruff: noqa: T201
"""Sanity-check leg pricing and portfolio maths against live pools.

Uniswap's sqrtPriceX96 decoding is easy to get subtly wrong (token0/token1 ordering, decimal
correction), and a wrong price silently corrupts every risk number downstream. This prints the
derived prices so they can be eyeballed against the real tickers:
    cd api && direnv exec . uv run --active python scripts/portfolio_check.py [walletAddress]
"""

import asyncio
import sys

from core.util import date_util

import _path_fix  # type: ignore[import-not-found]  # noqa: F401
from agent_barbell import constants
from agent_barbell.create_system_manager import create_system_manager
from agent_barbell.create_system_manager import use_system_manager
from agent_barbell.model import Barbell
from agent_barbell.system_manager import SystemManager

CHAIN_ID = constants.ROBINHOOD_CHAIN_ID
SGOV_PRICE_RANGE_USD = (95.0, 115.0)
GME_PRICE_RANGE_USD = (5.0, 100.0)


def _check_range(description: str, value: float, valueRange: tuple[float, float]) -> bool:
    isOk = valueRange[0] <= value <= valueRange[1]
    print(f'{"PASS" if isOk else "FAIL"}  {description}: ${value:,.4f} (expected ${valueRange[0]:,.0f}-${valueRange[1]:,.0f})')
    return isOk


async def do_stuff(systemManager: SystemManager, walletAddress: str) -> None:
    results: list[bool] = []
    anchorAddress = constants.CHAIN_ANCHOR_ASSET_MAP[CHAIN_ID]
    satelliteAddress = constants.CHAIN_SATELLITE_ASSET_MAP[CHAIN_ID]

    print('=== leg prices ===')
    pricesUsd = await systemManager.portfolioManager.get_leg_prices_usd(chainId=CHAIN_ID)
    results.append(_check_range('SGOV (anchor)', pricesUsd[anchorAddress], SGOV_PRICE_RANGE_USD))
    results.append(_check_range('GME (satellite)', pricesUsd[satelliteAddress], GME_PRICE_RANGE_USD))

    print(f'=== portfolio for {walletAddress} ===')
    currentDate = date_util.datetime_from_now()
    barbell = Barbell(
        barbellId='00000000-0000-0000-0000-000000000000',
        name='Portfolio check',
        createdDate=currentDate,
        updatedDate=currentDate,
        userId='00000000-0000-0000-0000-000000000000',
        chainId=CHAIN_ID,
        walletAddress=walletAddress,
        ownerAddress=walletAddress,
        anchorAssetAddress=anchorAddress,
        satelliteAssetAddress=satelliteAddress,
        isActive=True,
    )
    portfolio = await systemManager.portfolioManager.get_portfolio(barbell=barbell)
    for leg in (portfolio.anchor, portfolio.satellite, portfolio.cash):
        print(f'      {leg.symbol:<5} balance={leg.balance / (10**leg.decimals):,.6f} price=${leg.priceUsd:,.4f} value=${leg.valueUsd:,.2f}')
    print(f'      total=${portfolio.totalValueUsd:,.2f} satellite={portfolio.satelliteBps / 100:.2f}%')
    summedValue = portfolio.anchor.valueUsd + portfolio.satellite.valueUsd + portfolio.cash.valueUsd
    isTotalConsistent = abs(summedValue - portfolio.totalValueUsd) < 1e-6  # noqa: PLR2004
    print(f'{"PASS" if isTotalConsistent else "FAIL"}  legs sum to the reported total')
    results.append(isTotalConsistent)

    print()
    print(f'{sum(results)}/{len(results)} checks passed')


async def main() -> None:
    walletAddress = sys.argv[1] if len(sys.argv) > 1 else constants.ANCHOR_POOL_ADDRESS_MAP[CHAIN_ID]
    systemManager = create_system_manager()
    async with use_system_manager(systemManager=systemManager):
        await do_stuff(systemManager=systemManager, walletAddress=walletAddress)


if __name__ == '__main__':
    asyncio.run(main())
