from agent_barbell.agent.barbell_runtime_state import BarbellRuntimeState
from agent_barbell.agent.chat_tool import ChatTool
from agent_barbell.agent.chat_tool import ChatToolInput


class GetRiskStateInput(ChatToolInput):
    pass


class GetRiskStateTool(ChatTool[GetRiskStateInput, BarbellRuntimeState]):
    def __init__(self) -> None:
        super().__init__(
            name='get_risk_state',
            description=(
                "Get the deterministic risk engine's current reading: realized volatility, momentum, drawdown from peak, the satellite size it is targeting, and whether the kill switch has fired. "
                'Use this whenever the user asks about risk, volatility, how much they are down, or what the agent is about to do. The numbers here are computed by the engine, not by you — report them, do not recalculate them.'
            ),
            paramsSchema=GetRiskStateInput,
        )

    async def execute_inner(self, runtimeState: BarbellRuntimeState, params: GetRiskStateInput) -> str:  # noqa: ARG002
        riskState = await runtimeState.riskManager.get_risk_state(barbell=runtimeState.barbell)
        return self.data_to_markdown_yaml(
            data={
                'realizedVolatilityPercent': round(riskState.volatility * 100, 2),
                'momentumPercent': round(riskState.momentum * 100, 2),
                'drawdownPercent': round(riskState.drawdownBps / 100, 2),
                'lossBudgetPercent': round(riskState.currentSatelliteBps / 100, 2),
                'currentSatellitePercent': round(riskState.currentSatelliteBps / 100, 2),
                'targetSatellitePercent': round(riskState.targetSatelliteBps / 100, 2),
                'isKillSwitchTriggered': riskState.isKillSwitchTriggered,
                'shouldRebalance': riskState.shouldRebalance,
                'decisionTrace': riskState.decisionTrace,
            }
        )
