from typing import TypeVar

import yaml  # type: ignore[import-untyped]
from core import logging
from core.exceptions import KibaException
from core.util.typing_util import Json
from pydantic import BaseModel

from agent_barbell.agent.runtime_state import RuntimeState


class ChatToolInput(BaseModel):
    pass


ParamsType = TypeVar('ParamsType', bound=ChatToolInput)
RuntimeStateType = TypeVar('RuntimeStateType', bound=RuntimeState)
_ModelType = TypeVar('_ModelType', bound=BaseModel)


class ChatTool[ParamsType, RuntimeStateType](BaseModel):
    name: str
    description: str
    paramsSchema: type[ParamsType]

    async def execute_inner(self, runtimeState: RuntimeStateType, params: ParamsType) -> str:
        raise NotImplementedError('Subclasses must implement execute_inner')

    async def execute(self, runtimeState: RuntimeStateType, params: ParamsType) -> str:
        try:
            return await self.execute_inner(runtimeState=runtimeState, params=params)
        except KibaException as exception:
            logging.exception(exception)
            return f'Error during {self.name}: {exception.exceptionType} ({exception.message})'
        except Exception as exception:  # noqa: BLE001
            logging.exception(exception)
            return f'Error during {self.name}: {exception!s}'

    def model_to_markdown_yaml(self, model: _ModelType) -> str:
        return self.data_to_markdown_yaml(data=model.model_dump())

    def models_to_markdown_yaml(self, models: list[_ModelType]) -> str:
        return self.data_to_markdown_yaml(data=[model.model_dump() for model in models])

    def data_to_markdown_yaml(self, data: Json) -> str:
        return f'```yaml\n{yaml.dump(data=data, default_flow_style=False, sort_keys=False)}\n```'
