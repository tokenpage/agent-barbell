import uuid
from collections.abc import AsyncIterator

from core.store.database import Database

from agent_barbell.agent.barbell_runtime_state import BarbellRuntimeState
from agent_barbell.agent.chat_bot import LLM
from agent_barbell.agent.chat_bot import ChatBot
from agent_barbell.agent.chat_history_store import ChatHistoryStore
from agent_barbell.agent.runtime_state import RuntimeState
from agent_barbell.agent.tools.get_policy_tool import GetPolicyTool
from agent_barbell.agent.tools.get_portfolio_tool import GetPortfolioTool
from agent_barbell.agent.tools.get_risk_state_tool import GetRiskStateTool
from agent_barbell.agent.tools.set_risk_budget_tool import SetRiskBudgetTool
from agent_barbell.model import Barbell
from agent_barbell.model import ChatEvent
from agent_barbell.portfolio_manager import PortfolioManager
from agent_barbell.prompts import BARBELL_CREATION_STEP_PROMPT
from agent_barbell.prompts import BARBELL_CREATION_SYSTEM_PROMPT
from agent_barbell.prompts import BARBELL_STEP_PROMPT
from agent_barbell.prompts import BARBELL_SYSTEM_PROMPT
from agent_barbell.risk_manager import RiskManager

DEFAULT_CONVERSATION_ID = 'default'
_VISIBLE_EVENT_TYPES = {'user', 'agent'}


class ConversationManager:
    """Owns the chat loop and the tool set the language model is allowed to reach.

    Trimmed port of yieldseeker-app/api/agent_hack/conversation_manager.py.
    """

    def __init__(self, database: Database, llm: LLM, portfolioManager: PortfolioManager, riskManager: RiskManager) -> None:
        self.database = database
        self.llm = llm
        self.portfolioManager = portfolioManager
        self.riskManager = riskManager
        self.historyStore = ChatHistoryStore(database=database)
        self.creationChatBot = ChatBot(
            llm=llm,
            historyStore=self.historyStore,
            tools=[],
        )
        self.chatBot = ChatBot(
            llm=llm,
            historyStore=self.historyStore,
            tools=[GetPortfolioTool(), GetRiskStateTool(), GetPolicyTool(), SetRiskBudgetTool()],
        )

    async def add_creation_message(self, userId: str, conversationId: str, content: str, draftContext: str) -> AsyncIterator[ChatEvent]:
        draftBarbellId = str(uuid.uuid5(uuid.NAMESPACE_URL, f'agent-barbell:creation:{userId}'))
        runtimeState = RuntimeState(userId=userId, barbellId=draftBarbellId, conversationId=conversationId)
        creationMessage = f'Current barbell draft:\n{draftContext}\n\nUser question:\n{content}'
        async for event in self.creationChatBot.execute(
            systemPrompt=BARBELL_CREATION_SYSTEM_PROMPT,
            runtimeState=runtimeState,
            userMessage=creationMessage,
            prompt=BARBELL_CREATION_STEP_PROMPT,
        ):
            if event.eventType in _VISIBLE_EVENT_TYPES:
                yield event

    def _build_runtime_state(self, userId: str, barbell: Barbell, conversationId: str) -> BarbellRuntimeState:
        return BarbellRuntimeState(
            userId=userId,
            barbellId=barbell.barbellId,
            conversationId=conversationId,
            barbell=barbell,
            portfolioManager=self.portfolioManager,
            riskManager=self.riskManager,
        )

    async def list_chat_events(self, userId: str, barbellId: str, conversationId: str = DEFAULT_CONVERSATION_ID) -> list[ChatEvent]:
        events = await self.historyStore.list_events(userId=userId, barbellId=barbellId, conversationId=conversationId, maxEvents=100, shouldIncludeSteps=False, shouldIncludePrompts=False, shouldIncludeTools=False)
        return [event for event in events if event.eventType in _VISIBLE_EVENT_TYPES]

    async def add_user_message(self, userId: str, barbell: Barbell, content: str, conversationId: str = DEFAULT_CONVERSATION_ID) -> AsyncIterator[ChatEvent]:
        runtimeState = self._build_runtime_state(userId=userId, barbell=barbell, conversationId=conversationId)
        async for event in self.chatBot.execute(systemPrompt=BARBELL_SYSTEM_PROMPT, runtimeState=runtimeState, userMessage=content, prompt=BARBELL_STEP_PROMPT):
            if event.eventType in _VISIBLE_EVENT_TYPES:
                yield event
