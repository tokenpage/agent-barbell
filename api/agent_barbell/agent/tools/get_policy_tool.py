from agent_barbell.agent.barbell_runtime_state import BarbellRuntimeState
from agent_barbell.agent.chat_tool import ChatTool
from agent_barbell.agent.chat_tool import ChatToolInput


class GetPolicyInput(ChatToolInput):
    pass


class GetPolicyTool(ChatTool[GetPolicyInput, BarbellRuntimeState]):
    def __init__(self) -> None:
        super().__init__(
            name='get_policy',
            description='Get the risk budget currently in force: the maximum drawdown from peak, the satellite target, and the satellite cap. Use this before proposing any change to the budget, so you can tell the user what they have today.',
            paramsSchema=GetPolicyInput,
        )

    async def execute_inner(self, runtimeState: BarbellRuntimeState, params: GetPolicyInput) -> str:  # noqa: ARG002
        policy = await runtimeState.riskManager.get_effective_policy(barbellId=runtimeState.barbellId)
        storedPolicy = await runtimeState.riskManager.get_policy_or_none(barbellId=runtimeState.barbellId)
        return self.data_to_markdown_yaml(
            data={
                'maxDrawdownPercent': round(policy.maxDrawdownBps / 100, 2),
                'targetSatellitePercent': round(policy.targetSatelliteBps / 100, 2),
                'maxSatellitePercent': round(policy.maxSatelliteBps / 100, 2),
                'isDefault': storedPolicy is None,
                'isKilled': storedPolicy.isKilled if storedPolicy is not None else False,
            }
        )
