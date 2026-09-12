from pydantic import Field

from agent_barbell import constants
from agent_barbell.agent.barbell_runtime_state import BarbellRuntimeState
from agent_barbell.agent.chat_tool import ChatTool
from agent_barbell.agent.chat_tool import ChatToolInput


class SetRiskBudgetInput(ChatToolInput):
    maxDrawdownPercent: float = Field(..., description=f'The most the account may fall from its peak before the kill switch sells the satellite leg entirely. Between {constants.MIN_MAX_DRAWDOWN_BPS / 100} and {constants.MAX_MAX_DRAWDOWN_BPS / 100}.')
    targetSatellitePercent: float = Field(..., description='The share of the account the user wants in the volatile satellite leg in normal conditions. The engine scales this by realized volatility; it is a starting point, not a fixed weight.')
    maxSatellitePercent: float = Field(..., description='A hard cap on the satellite leg. The engine may never size above this regardless of how attractive conditions look.')


class SetRiskBudgetTool(ChatTool[SetRiskBudgetInput, BarbellRuntimeState]):
    """The only tool that writes anything.

    It sets *bounds*. It does not size a position, place a trade, or clear a kill switch — the
    deterministic engine does the sizing inside these bounds, and only the wallet owner can
    re-arm a fired kill switch on-chain. Per plans/agent-types-overview.md: "Language-model
    reasoning must not replace hard transaction, asset, liquidity, or safety controls."
    """

    def __init__(self) -> None:
        super().__init__(
            name='set_risk_budget',
            description=(
                'Set the risk budget for the barbell. Use this when the user states how much they are willing to lose, or asks to change how aggressive the agent is. '
                'Always call get_policy first and confirm the change with the user before calling this. '
                'This sets limits only — the engine decides the actual position size within them, and you must not promise a specific trade.'
            ),
            paramsSchema=SetRiskBudgetInput,
        )

    async def execute_inner(self, runtimeState: BarbellRuntimeState, params: SetRiskBudgetInput) -> str:
        policy = await runtimeState.riskManager.set_policy(
            barbellId=runtimeState.barbellId,
            maxDrawdownBps=int(params.maxDrawdownPercent * 100),
            targetSatelliteBps=int(params.targetSatellitePercent * 100),
            maxSatelliteBps=int(params.maxSatellitePercent * 100),
        )
        riskState = await runtimeState.riskManager.get_risk_state(barbell=runtimeState.barbell)
        return self.data_to_markdown_yaml(
            data={
                'savedMaxDrawdownPercent': round(policy.maxDrawdownBps / 100, 2),
                'savedTargetSatellitePercent': round(policy.targetSatelliteBps / 100, 2),
                'savedMaxSatellitePercent': round(policy.maxSatelliteBps / 100, 2),
                'wasClamped': int(params.maxDrawdownPercent * 100) != policy.maxDrawdownBps,
                'engineTargetSatellitePercentNow': round(riskState.targetSatelliteBps / 100, 2),
                'engineDecisionTrace': riskState.decisionTrace,
            }
        )
