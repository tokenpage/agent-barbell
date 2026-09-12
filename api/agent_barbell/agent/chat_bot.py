from collections.abc import AsyncIterator
from typing import Any

from core import logging
from core.util import json_util
from core.util.typing_util import JsonObject

from agent_barbell import constants
from agent_barbell.agent.chat_history_store import ChatHistoryStore
from agent_barbell.agent.chat_tool import ChatTool
from agent_barbell.agent.runtime_state import RuntimeState
from agent_barbell.model import ChatEvent


class LLM:
    async def get_query(self, systemPrompt: str, prompt: str) -> JsonObject:
        raise NotImplementedError('Subclasses must implement get_query')

    async def get_next_step(self, promptQuery: JsonObject) -> JsonObject:
        raise NotImplementedError('Subclasses must implement get_next_step')


class ChatBot:
    def __init__(self, llm: LLM, historyStore: ChatHistoryStore, tools: list[ChatTool[Any, Any]]) -> None:  # type: ignore[explicit-any]
        self.llm = llm
        self.historyStore = historyStore
        self.tools = tools

    async def execute(self, systemPrompt: str, runtimeState: RuntimeState, userMessage: str, prompt: str) -> AsyncIterator[ChatEvent]:
        previousEvents = await self.historyStore.list_events(userId=runtimeState.userId, barbellId=runtimeState.barbellId, conversationId=runtimeState.conversationId, maxEvents=50, shouldIncludeSteps=False, shouldIncludePrompts=False, shouldIncludeTools=False)
        toolDescriptions = '\n'.join([f'{tool.name}: {tool.description}\n  Parameters: {json_util.dumps(tool.paramsSchema.model_json_schema())}' for tool in self.tools])
        eventStrings = [f'{event.eventType}: {json_util.dumps(event.content) if isinstance(event.content, dict) else event.content}' for event in previousEvents]
        historyContext = '\n'.join([eventString.replace('\n', '  ') for eventString in eventStrings]).strip()
        yield await self.historyStore.add_event(userId=runtimeState.userId, barbellId=runtimeState.barbellId, conversationId=runtimeState.conversationId, eventType='user', content=userMessage)
        isComplete = False
        currentContext = ''
        lastMessage = None
        stepCount = 0
        while not isComplete:
            stepCount += 1
            if stepCount > constants.AGENT_CHAT_MAX_STEPS:
                logging.error(f'Agent exceeded {constants.AGENT_CHAT_MAX_STEPS} steps, ending to prevent a runaway loop')
                yield await self.historyStore.add_event(
                    userId=runtimeState.userId, barbellId=runtimeState.barbellId, conversationId=runtimeState.conversationId, eventType='agent', content="Sorry, I wasn't able to finish that. Could you try rephrasing or asking a more specific question?"
                )
                break
            formattedPrompt = prompt.format(historyContext=historyContext, currentContext=currentContext.strip() or '(empty)', tools=toolDescriptions, userMessage=userMessage)
            promptQuery = await self.llm.get_query(systemPrompt=systemPrompt, prompt=formattedPrompt)
            yield await self.historyStore.add_event(userId=runtimeState.userId, barbellId=runtimeState.barbellId, conversationId=runtimeState.conversationId, eventType='prompt', content=promptQuery)
            step = await self.llm.get_next_step(promptQuery=promptQuery)
            yield await self.historyStore.add_event(userId=runtimeState.userId, barbellId=runtimeState.barbellId, conversationId=runtimeState.conversationId, eventType='step', content=step)
            isComplete = bool(step.get('isComplete', False))
            if step.get('tool'):
                tool = next(tool for tool in self.tools if tool.name == step['tool'])
                params = tool.paramsSchema(**step['args'])  # type: ignore[arg-type]
                result = await tool.execute(runtimeState=runtimeState, params=params)
                resultMessage = f'{step["tool"]} complete, result: {result}'
                yield await self.historyStore.add_event(userId=runtimeState.userId, barbellId=runtimeState.barbellId, conversationId=runtimeState.conversationId, eventType='tool', content=resultMessage)
                currentContext += f'\nTool: {resultMessage}'
                isComplete = False
            elif step.get('message'):
                currentMessage = str(step['message'])
                if currentMessage == lastMessage:
                    logging.error('LLM repeated the same message, ending to prevent infinite loop')
                    isComplete = True
                else:
                    yield await self.historyStore.add_event(userId=runtimeState.userId, barbellId=runtimeState.barbellId, conversationId=runtimeState.conversationId, eventType='agent', content=currentMessage)
                    currentContext += f'\nAgent: {currentMessage}'
                    lastMessage = currentMessage
            else:
                logging.error('LLM step did not contain tool or message')
