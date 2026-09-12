"""Deterministic risk engine.

Pure functions over inputs, no I/O, no language model. From plans/agent-types-overview.md:
"Language-model reasoning must not replace hard transaction, asset, liquidity, or safety
controls." The LLM translates intent into a bounded policy; everything that decides how much
risk is actually held, and when to cut it, happens here.

Modelled structurally on yieldseeker-app/api/agent_hack/rule_compiler.py.
"""

import datetime
import itertools
import math

from pydantic import BaseModel

from agent_barbell import constants
from agent_barbell.model import PriceTick
from agent_barbell.model import RiskSnapshot

_TRADING_DAYS_PER_YEAR = 252
_MIN_TICKS_FOR_VOLATILITY = 3


class RiskPolicy(BaseModel):
    maxDrawdownBps: int
    targetSatelliteBps: int
    maxSatelliteBps: int


class RiskState(BaseModel):
    """Every intermediate the engine used, so the UI and the LLM can both explain the decision.

    The decisionTrace idea is borrowed from plans/agent-type-borrowing.md.
    """

    volatility: float
    momentum: float
    peakValueUsd: float
    totalValueUsd: float
    drawdownBps: int
    currentSatelliteBps: int
    targetSatelliteBps: int
    isKillSwitchTriggered: bool
    shouldRebalance: bool
    decisionTrace: str


def calculate_realized_volatility(priceTicks: list[PriceTick], windowDays: int = constants.VOLATILITY_WINDOW_DAYS) -> float:
    """Annualised stdev of log returns over the trailing window."""
    if len(priceTicks) < _MIN_TICKS_FOR_VOLATILITY:
        return 0.0
    sortedTicks = sorted(priceTicks, key=lambda tick: tick.blockDate)
    cutoffDate = sortedTicks[-1].blockDate - datetime.timedelta(days=windowDays)
    windowTicks = [tick for tick in sortedTicks if tick.blockDate >= cutoffDate]
    if len(windowTicks) < _MIN_TICKS_FOR_VOLATILITY:
        return 0.0
    logReturns = [math.log(later.priceUsd / earlier.priceUsd) for earlier, later in itertools.pairwise(windowTicks) if earlier.priceUsd > 0 and later.priceUsd > 0]
    if len(logReturns) < 2:  # noqa: PLR2004
        return 0.0
    meanReturn = sum(logReturns) / len(logReturns)
    variance = sum((logReturn - meanReturn) ** 2 for logReturn in logReturns) / (len(logReturns) - 1)
    periodsPerDay = max(1.0, len(logReturns) / max(1.0, windowDays))
    return math.sqrt(variance) * math.sqrt(_TRADING_DAYS_PER_YEAR * periodsPerDay)


def calculate_momentum(priceTicks: list[PriceTick], windowDays: int = constants.MOMENTUM_WINDOW_DAYS) -> float:
    """Trailing simple return over the window. Positive means the leg is trending up."""
    if len(priceTicks) < 2:  # noqa: PLR2004
        return 0.0
    sortedTicks = sorted(priceTicks, key=lambda tick: tick.blockDate)
    cutoffDate = sortedTicks[-1].blockDate - datetime.timedelta(days=windowDays)
    windowTicks = [tick for tick in sortedTicks if tick.blockDate >= cutoffDate]
    if len(windowTicks) < 2 or windowTicks[0].priceUsd <= 0:  # noqa: PLR2004
        return 0.0
    return (windowTicks[-1].priceUsd / windowTicks[0].priceUsd) - 1.0


def calculate_peak_value_usd(snapshots: list[RiskSnapshot], currentValueUsd: float) -> float:
    return max([currentValueUsd, *[snapshot.totalValueUsd for snapshot in snapshots]])


def calculate_drawdown_bps(peakValueUsd: float, currentValueUsd: float) -> int:
    """The number the whole product exists to defend."""
    if peakValueUsd <= 0:
        return 0
    drawdown = (peakValueUsd - currentValueUsd) / peakValueUsd
    return max(0, min(constants.MAX_BPS, math.floor(drawdown * constants.MAX_BPS)))


def calculate_target_satellite_bps(policy: RiskPolicy, volatility: float, momentum: float, drawdownBps: int) -> int:
    """Volatility targeting with a momentum overlay, hard-clamped by the policy.

    The kill switch is not a suggestion: once drawdown reaches the budget the satellite target
    is zero and no amount of favourable volatility or momentum can lift it.
    """
    if drawdownBps >= policy.maxDrawdownBps:
        return 0
    volatilityScaledBps = policy.targetSatelliteBps if volatility <= 0 else int(policy.targetSatelliteBps * (constants.TARGET_PORTFOLIO_VOLATILITY / volatility))
    # Momentum only ever tilts within +/-25% of the volatility-scaled size.
    momentumMultiplier = 1.0 + max(-0.25, min(0.25, momentum))
    targetBps = int(volatilityScaledBps * momentumMultiplier)
    # Taper as the budget is approached rather than waiting for a cliff edge.
    remainingBudgetRatio = 1.0 - (drawdownBps / policy.maxDrawdownBps)
    targetBps = int(targetBps * remainingBudgetRatio)
    return max(0, min(policy.maxSatelliteBps, targetBps))


def build_risk_state(
    policy: RiskPolicy,
    satellitePriceTicks: list[PriceTick],
    snapshots: list[RiskSnapshot],
    totalValueUsd: float,
    currentSatelliteBps: int,
) -> RiskState:
    volatility = calculate_realized_volatility(priceTicks=satellitePriceTicks)
    momentum = calculate_momentum(priceTicks=satellitePriceTicks)
    peakValueUsd = calculate_peak_value_usd(snapshots=snapshots, currentValueUsd=totalValueUsd)
    drawdownBps = calculate_drawdown_bps(peakValueUsd=peakValueUsd, currentValueUsd=totalValueUsd)
    targetSatelliteBps = calculate_target_satellite_bps(policy=policy, volatility=volatility, momentum=momentum, drawdownBps=drawdownBps)
    isKillSwitchTriggered = drawdownBps >= policy.maxDrawdownBps
    # Threshold-based, not continuous. From plans/agent-type-rebalancing.md: "Research favors
    # frequent monitoring with relatively infrequent threshold-based trades."
    shouldRebalance = isKillSwitchTriggered or abs(targetSatelliteBps - currentSatelliteBps) >= constants.REBALANCE_BAND_BPS
    if isKillSwitchTriggered:
        decisionTrace = f'Drawdown {drawdownBps / 100:.2f}% reached the {policy.maxDrawdownBps / 100:.2f}% budget. Kill switch: satellite target forced to 0%.'
    elif shouldRebalance:
        decisionTrace = (
            f'Realized vol {volatility:.2%} vs {constants.TARGET_PORTFOLIO_VOLATILITY:.0%} target and momentum {momentum:+.2%} '
            f'size the satellite at {targetSatelliteBps / 100:.2f}%, against {currentSatelliteBps / 100:.2f}% held. '
            f'Drawdown is {drawdownBps / 100:.2f}% of a {policy.maxDrawdownBps / 100:.2f}% budget. '
            f'Gap exceeds the {constants.REBALANCE_BAND_BPS / 100:.2f}% rebalance band, so a trade is warranted.'
        )
    else:
        decisionTrace = (
            f'Realized vol {volatility:.2%}, momentum {momentum:+.2%}, drawdown {drawdownBps / 100:.2f}% of a {policy.maxDrawdownBps / 100:.2f}% budget. '
            f'Satellite target {targetSatelliteBps / 100:.2f}% is within the {constants.REBALANCE_BAND_BPS / 100:.2f}% band of the {currentSatelliteBps / 100:.2f}% held. Holding.'
        )
    return RiskState(
        volatility=volatility,
        momentum=momentum,
        peakValueUsd=peakValueUsd,
        totalValueUsd=totalValueUsd,
        drawdownBps=drawdownBps,
        currentSatelliteBps=currentSatelliteBps,
        targetSatelliteBps=targetSatelliteBps,
        isKillSwitchTriggered=isKillSwitchTriggered,
        shouldRebalance=shouldRebalance,
        decisionTrace=decisionTrace,
    )
