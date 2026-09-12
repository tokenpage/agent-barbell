# ruff: noqa: T201
"""Exercise the deterministic risk engine against synthetic price paths.

The one claim the whole pitch rests on is that the kill switch is not the language model's
decision. This proves it in isolation, with no database and no chain:
    cd api && uv run --active python scripts/risk_engine_check.py
"""

import datetime
import uuid

from core.util import date_util

import _path_fix  # type: ignore[import-not-found]  # noqa: F401
from agent_barbell import constants
from agent_barbell import risk_engine
from agent_barbell.model import PriceTick
from agent_barbell.model import RiskSnapshot

CHAIN_ID = constants.ROBINHOOD_CHAIN_ID
MIN_CHOPPY_VOLATILITY = 0.5


def _ticks(prices: list[float]) -> list[PriceTick]:
    startDate = date_util.datetime_from_now(days=-len(prices))
    return [
        PriceTick(
            priceTickId=str(uuid.uuid4()),
            createdDate=startDate,
            updatedDate=startDate,
            chainId=CHAIN_ID,
            assetAddress=constants.CHAIN_SATELLITE_ASSET_MAP[CHAIN_ID],
            blockNumber=index,
            blockDate=startDate + datetime.timedelta(days=index),
            priceUsd=price,
        )
        for index, price in enumerate(prices)
    ]


def _snapshots(values: list[float]) -> list[RiskSnapshot]:
    startDate = date_util.datetime_from_now(days=-len(values))
    return [
        RiskSnapshot(
            riskSnapshotId=str(uuid.uuid4()),
            createdDate=startDate,
            updatedDate=startDate,
            barbellId=str(uuid.uuid4()),
            snapshotDate=startDate + datetime.timedelta(days=index),
            totalValueUsd=value,
            anchorValueUsd=value * 0.8,
            satelliteValueUsd=value * 0.2,
            cashValueUsd=0,
            satelliteBps=2000,
            peakValueUsd=value,
            drawdownBps=0,
            volatility=0,
            momentum=0,
            targetSatelliteBps=2000,
        )
        for index, value in enumerate(values)
    ]


def _check(description: str, actual: object, expected: object) -> bool:
    isOk = actual == expected
    print(f'{"PASS" if isOk else "FAIL"}  {description}')
    if not isOk:
        print(f'        expected: {expected}')
        print(f'        actual:   {actual}')
    return isOk


def main() -> None:
    policy = risk_engine.RiskPolicy(maxDrawdownBps=1500, targetSatelliteBps=2000, maxSatelliteBps=4000)
    results: list[bool] = []

    print('=== volatility ===')
    flatVolatility = risk_engine.calculate_realized_volatility(priceTicks=_ticks([100.0] * 20))
    results.append(_check('flat prices give zero volatility', flatVolatility, 0.0))
    choppyVolatility = risk_engine.calculate_realized_volatility(priceTicks=_ticks([100, 110, 95, 120, 90, 130, 85, 125, 92, 118, 88, 124, 91, 119]))
    print(f'      choppy path volatility: {choppyVolatility:.2%}')
    results.append(_check('choppy prices give non-zero volatility', choppyVolatility > MIN_CHOPPY_VOLATILITY, True))

    print('=== momentum ===')
    upMomentum = risk_engine.calculate_momentum(priceTicks=_ticks([100, 102, 104, 106, 108, 110]))
    print(f'      rising path momentum: {upMomentum:+.2%}')
    results.append(_check('rising prices give positive momentum', upMomentum > 0, True))
    downMomentum = risk_engine.calculate_momentum(priceTicks=_ticks([110, 108, 106, 104, 102, 100]))
    results.append(_check('falling prices give negative momentum', downMomentum < 0, True))

    print('=== drawdown ===')
    results.append(_check('no drawdown at the peak', risk_engine.calculate_drawdown_bps(peakValueUsd=1000, currentValueUsd=1000), 0))
    results.append(_check('20% fall is 2000bps', risk_engine.calculate_drawdown_bps(peakValueUsd=1000, currentValueUsd=800), 2000))

    print('=== kill switch ===')
    results.append(_check('target is zero once drawdown reaches the budget', risk_engine.calculate_target_satellite_bps(policy=policy, volatility=0.2, momentum=0.5, drawdownBps=1500), 0))
    results.append(_check('target is zero beyond the budget', risk_engine.calculate_target_satellite_bps(policy=policy, volatility=0.05, momentum=1.0, drawdownBps=9000), 0))
    results.append(_check('target is non-zero inside the budget', risk_engine.calculate_target_satellite_bps(policy=policy, volatility=0.2, momentum=0.0, drawdownBps=0) > 0, True))
    results.append(_check('target never exceeds maxSatelliteBps', risk_engine.calculate_target_satellite_bps(policy=policy, volatility=0.001, momentum=0.25, drawdownBps=0) <= policy.maxSatelliteBps, True))

    print('=== sizing ===')
    lowVolTarget = risk_engine.calculate_target_satellite_bps(policy=policy, volatility=0.10, momentum=0.0, drawdownBps=0)
    highVolTarget = risk_engine.calculate_target_satellite_bps(policy=policy, volatility=0.80, momentum=0.0, drawdownBps=0)
    print(f'      vol 10% -> {lowVolTarget}bps, vol 80% -> {highVolTarget}bps')
    results.append(_check('higher volatility means a smaller satellite', highVolTarget < lowVolTarget, True))

    print('=== end to end: a 20% crash against a 15% budget ===')
    crashTicks = _ticks([100, 99, 101, 98, 100, 97, 95, 90, 86, 82, 80])
    crashSnapshots = _snapshots([1000, 1005, 1010, 1000, 980, 950, 900, 860, 820, 800])
    state = risk_engine.build_risk_state(policy=policy, satellitePriceTicks=crashTicks, snapshots=crashSnapshots, totalValueUsd=800.0, currentSatelliteBps=2000)
    print(f'      {state.decisionTrace}')
    results.append(_check('kill switch fires', state.isKillSwitchTriggered, True))
    results.append(_check('satellite target is zero', state.targetSatelliteBps, 0))
    results.append(_check('a rebalance is demanded', state.shouldRebalance, True))
    results.append(_check('peak is the running maximum', state.peakValueUsd, 1010.0))

    print('=== end to end: a calm market inside the budget ===')
    calmTicks = _ticks([100, 100.4, 100.1, 100.6, 100.3, 100.8, 100.5, 100.9])
    calmSnapshots = _snapshots([1000, 1002, 1001, 1004, 1003, 1005])
    calmState = risk_engine.build_risk_state(policy=policy, satellitePriceTicks=calmTicks, snapshots=calmSnapshots, totalValueUsd=1005.0, currentSatelliteBps=2000)
    print(f'      {calmState.decisionTrace}')
    results.append(_check('kill switch stays armed but unfired', calmState.isKillSwitchTriggered, False))

    print()
    print(f'{sum(results)}/{len(results)} checks passed')
    if not all(results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
