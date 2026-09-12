from core.store.database import Database
from core.store.retriever import Direction
from core.store.retriever import IntegerFieldFilter
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import date_util

from agent_barbell import constants
from agent_barbell import risk_engine
from agent_barbell.model import Barbell
from agent_barbell.model import BarbellPolicy
from agent_barbell.model import PriceTick
from agent_barbell.model import RiskSnapshot
from agent_barbell.portfolio_manager import Portfolio
from agent_barbell.portfolio_manager import PortfolioManager
from agent_barbell.risk_engine import RiskPolicy
from agent_barbell.risk_engine import RiskState
from agent_barbell.store import schema
from agent_barbell.store.entity_repository import UUIDFieldFilter

_MAX_PRICE_TICKS = 5000
_MAX_SNAPSHOTS = 1000


class RiskManager:
    """Orchestration only. Every number is computed by risk_engine, which has no I/O.

    Follows the manager conventions of yieldseeker-app/api/agent_hack/stats_manager.py.
    """

    def __init__(self, database: Database, portfolioManager: PortfolioManager) -> None:
        self.database = database
        self.portfolioManager = portfolioManager

    async def get_policy_or_none(self, barbellId: str) -> BarbellPolicy | None:
        return await schema.BarbellPoliciesRepository.get_first(
            database=self.database,
            fieldFilters=[UUIDFieldFilter(fieldName=schema.BarbellPoliciesTable.c.barbellId.key, eq=barbellId)],
            orders=[Order(fieldName=schema.BarbellPoliciesTable.c.createdDate.key, direction=Direction.DESCENDING)],
        )

    async def get_effective_policy(self, barbellId: str) -> RiskPolicy:
        policy = await self.get_policy_or_none(barbellId=barbellId)
        if policy is None:
            return RiskPolicy(
                maxDrawdownBps=constants.DEFAULT_MAX_DRAWDOWN_BPS,
                targetSatelliteBps=constants.DEFAULT_TARGET_SATELLITE_BPS,
                maxSatelliteBps=constants.DEFAULT_MAX_SATELLITE_BPS,
            )
        return RiskPolicy(maxDrawdownBps=policy.maxDrawdownBps, targetSatelliteBps=policy.targetSatelliteBps, maxSatelliteBps=policy.maxSatelliteBps)

    async def set_policy(self, barbellId: str, maxDrawdownBps: int, targetSatelliteBps: int, maxSatelliteBps: int, transactionHash: str | None = None) -> BarbellPolicy:
        clampedMaxDrawdownBps = max(constants.MIN_MAX_DRAWDOWN_BPS, min(constants.MAX_MAX_DRAWDOWN_BPS, maxDrawdownBps))
        clampedMaxSatelliteBps = max(0, min(constants.MAX_BPS, maxSatelliteBps))
        clampedTargetSatelliteBps = max(0, min(clampedMaxSatelliteBps, targetSatelliteBps))
        return await schema.BarbellPoliciesRepository.create(
            database=self.database,
            barbellId=barbellId,
            maxDrawdownBps=clampedMaxDrawdownBps,
            targetSatelliteBps=clampedTargetSatelliteBps,
            maxSatelliteBps=clampedMaxSatelliteBps,
            isKilled=False,
            transactionHash=transactionHash,
        )

    async def list_price_ticks(self, chainId: int, assetAddress: str) -> list[PriceTick]:
        return await schema.PriceTicksRepository.list_many(
            database=self.database,
            fieldFilters=[
                IntegerFieldFilter(fieldName=schema.PriceTicksTable.c.chainId.key, eq=chainId),
                StringFieldFilter(fieldName=schema.PriceTicksTable.c.assetAddress.key, eq=assetAddress),
            ],
            orders=[Order(fieldName=schema.PriceTicksTable.c.blockDate.key, direction=Direction.DESCENDING)],
            limit=_MAX_PRICE_TICKS,
        )

    async def list_snapshots(self, barbellId: str) -> list[RiskSnapshot]:
        return await schema.RiskSnapshotsRepository.list_many(
            database=self.database,
            fieldFilters=[UUIDFieldFilter(fieldName=schema.RiskSnapshotsTable.c.barbellId.key, eq=barbellId)],
            orders=[Order(fieldName=schema.RiskSnapshotsTable.c.snapshotDate.key, direction=Direction.DESCENDING)],
            limit=_MAX_SNAPSHOTS,
        )

    async def get_risk_state(self, barbell: Barbell, portfolio: Portfolio | None = None) -> RiskState:
        resolvedPortfolio = portfolio if portfolio is not None else await self.portfolioManager.get_portfolio(barbell=barbell)
        policy = await self.get_effective_policy(barbellId=barbell.barbellId)
        satellitePriceTicks = await self.list_price_ticks(chainId=barbell.chainId, assetAddress=barbell.satelliteAssetAddress)
        snapshots = await self.list_snapshots(barbellId=barbell.barbellId)
        return risk_engine.build_risk_state(
            policy=policy,
            satellitePriceTicks=satellitePriceTicks,
            snapshots=snapshots,
            totalValueUsd=resolvedPortfolio.totalValueUsd,
            currentSatelliteBps=resolvedPortfolio.satelliteBps,
        )

    async def record_snapshot(self, barbell: Barbell) -> RiskSnapshot:
        portfolio = await self.portfolioManager.get_portfolio(barbell=barbell)
        riskState = await self.get_risk_state(barbell=barbell, portfolio=portfolio)
        return await schema.RiskSnapshotsRepository.create(
            database=self.database,
            barbellId=barbell.barbellId,
            snapshotDate=date_util.datetime_from_now(),
            totalValueUsd=portfolio.totalValueUsd,
            anchorValueUsd=portfolio.anchor.valueUsd,
            satelliteValueUsd=portfolio.satellite.valueUsd,
            cashValueUsd=portfolio.cash.valueUsd,
            satelliteBps=portfolio.satelliteBps,
            peakValueUsd=riskState.peakValueUsd,
            drawdownBps=riskState.drawdownBps,
            volatility=riskState.volatility,
            momentum=riskState.momentum,
            targetSatelliteBps=riskState.targetSatelliteBps,
        )
