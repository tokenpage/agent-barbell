from agent_barbell import model
from agent_barbell.api import v1_resources as resources
from agent_barbell.portfolio_manager import LegBalance
from agent_barbell.portfolio_manager import Portfolio
from agent_barbell.risk_engine import RiskState
from agent_barbell.risk_manager import RiskManager
from agent_barbell.wallet_manager import WalletManager


class ResourceBuilderV1:
    """Converts domain models into API resources. Managers never return resources directly.

    Mirrors yieldseeker-app/api/agent_hack/api/v1_resource_builder.py.
    """

    def __init__(self, walletManager: WalletManager, riskManager: RiskManager) -> None:
        self.walletManager = walletManager
        self.riskManager = riskManager

    def user_from_model(self, user: model.User) -> resources.User:
        return resources.User(userId=user.userId, walletAddress=user.walletAddress, username=user.username)

    async def barbell_from_model(self, barbell: model.Barbell) -> resources.Barbell:
        isWalletDeployed = await self.walletManager.is_wallet_deployed(barbell=barbell)
        return resources.Barbell(
            barbellId=barbell.barbellId,
            name=barbell.name,
            chainId=barbell.chainId,
            walletAddress=barbell.walletAddress,
            ownerAddress=barbell.ownerAddress,
            anchorAssetAddress=barbell.anchorAssetAddress,
            satelliteAssetAddress=barbell.satelliteAssetAddress,
            isWalletDeployed=isWalletDeployed,
            createdDate=barbell.createdDate,
        )

    def portfolio_from_model(self, portfolio: Portfolio) -> resources.Portfolio:
        return resources.Portfolio(
            chainId=portfolio.chainId,
            walletAddress=portfolio.walletAddress,
            anchor=self._leg_from_model(leg=portfolio.anchor),
            satellite=self._leg_from_model(leg=portfolio.satellite),
            cash=self._leg_from_model(leg=portfolio.cash),
            totalValueUsd=portfolio.totalValueUsd,
            satelliteBps=portfolio.satelliteBps,
        )

    def _leg_from_model(self, leg: LegBalance) -> resources.LegBalance:
        return resources.LegBalance(
            assetAddress=leg.assetAddress,
            symbol=leg.symbol,
            decimals=leg.decimals,
            balance=str(leg.balance),
            priceUsd=leg.priceUsd,
            valueUsd=leg.valueUsd,
        )

    async def policy_resource(self, barbellId: str) -> resources.RiskPolicy:
        policy = await self.riskManager.get_policy_or_none(barbellId=barbellId)
        if policy is None:
            effectivePolicy = await self.riskManager.get_effective_policy(barbellId=barbellId)
            return resources.RiskPolicy(
                maxDrawdownBps=effectivePolicy.maxDrawdownBps,
                targetSatelliteBps=effectivePolicy.targetSatelliteBps,
                maxSatelliteBps=effectivePolicy.maxSatelliteBps,
                isKilled=False,
                transactionHash=None,
            )
        return resources.RiskPolicy(
            maxDrawdownBps=policy.maxDrawdownBps,
            targetSatelliteBps=policy.targetSatelliteBps,
            maxSatelliteBps=policy.maxSatelliteBps,
            isKilled=policy.isKilled,
            transactionHash=policy.transactionHash,
        )

    def risk_state_from_model(self, riskState: RiskState, policy: resources.RiskPolicy) -> resources.RiskState:
        return resources.RiskState(
            volatility=riskState.volatility,
            momentum=riskState.momentum,
            peakValueUsd=riskState.peakValueUsd,
            totalValueUsd=riskState.totalValueUsd,
            drawdownBps=riskState.drawdownBps,
            currentSatelliteBps=riskState.currentSatelliteBps,
            targetSatelliteBps=riskState.targetSatelliteBps,
            isKillSwitchTriggered=riskState.isKillSwitchTriggered,
            shouldRebalance=riskState.shouldRebalance,
            decisionTrace=riskState.decisionTrace,
            policy=policy,
        )

    def snapshot_from_model(self, snapshot: model.RiskSnapshot) -> resources.RiskSnapshot:
        return resources.RiskSnapshot(
            snapshotDate=snapshot.snapshotDate,
            totalValueUsd=snapshot.totalValueUsd,
            satelliteBps=snapshot.satelliteBps,
            drawdownBps=snapshot.drawdownBps,
            volatility=snapshot.volatility,
            momentum=snapshot.momentum,
            targetSatelliteBps=snapshot.targetSatelliteBps,
        )

    def chat_message_from_model(self, chatEvent: model.ChatEvent) -> resources.ChatMessage:
        return resources.ChatMessage(
            chatEventId=chatEvent.chatEventId,
            createdDate=chatEvent.createdDate,
            content=chatEvent.content if isinstance(chatEvent.content, str) else str(chatEvent.content),
            isUser=chatEvent.eventType == 'user',
        )

    def action_from_model(self, action: model.BarbellAction) -> resources.BarbellAction:
        return resources.BarbellAction(
            barbellActionId=action.barbellActionId,
            createdDate=action.createdDate,
            actionType=action.actionType,
            fromSatelliteBps=action.fromSatelliteBps,
            toSatelliteBps=action.toSatelliteBps,
            reason=action.reason,
            decisionTrace=action.decisionTrace,
            transactionHash=action.transactionHash,
        )
