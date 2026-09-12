from agent_barbell.agent.barbell_runtime_state import BarbellRuntimeState
from agent_barbell.agent.chat_tool import ChatTool
from agent_barbell.agent.chat_tool import ChatToolInput


class GetPortfolioInput(ChatToolInput):
    pass


class GetPortfolioTool(ChatTool[GetPortfolioInput, BarbellRuntimeState]):
    def __init__(self) -> None:
        super().__init__(
            name='get_portfolio',
            description='Get the current holdings of the barbell: the anchor leg, the satellite leg, and uninvested cash, each with a USD value. Use this whenever the user asks what they hold or what their account is worth.',
            paramsSchema=GetPortfolioInput,
        )

    async def execute_inner(self, runtimeState: BarbellRuntimeState, params: GetPortfolioInput) -> str:  # noqa: ARG002
        portfolio = await runtimeState.portfolioManager.get_portfolio(barbell=runtimeState.barbell)
        return self.data_to_markdown_yaml(
            data={
                'totalValueUsd': round(portfolio.totalValueUsd, 2),
                'satellitePercent': round(portfolio.satelliteBps / 100, 2),
                'legs': [
                    {'leg': 'anchor', 'symbol': portfolio.anchor.symbol, 'valueUsd': round(portfolio.anchor.valueUsd, 2), 'priceUsd': round(portfolio.anchor.priceUsd, 4)},
                    {'leg': 'satellite', 'symbol': portfolio.satellite.symbol, 'valueUsd': round(portfolio.satellite.valueUsd, 2), 'priceUsd': round(portfolio.satellite.priceUsd, 4)},
                    {'leg': 'cash', 'symbol': portfolio.cash.symbol, 'valueUsd': round(portfolio.cash.valueUsd, 2), 'priceUsd': round(portfolio.cash.priceUsd, 4)},
                ],
            }
        )
