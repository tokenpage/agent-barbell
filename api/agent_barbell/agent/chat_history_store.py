import datetime

import sqlalchemy
from core.store.database import Database
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import date_util
from core.util.typing_util import JsonObject

from agent_barbell.model import ChatEvent
from agent_barbell.store import schema


class ChatHistoryStore:
    def __init__(self, database: Database) -> None:
        self.database = database

    async def add_event(self, userId: str, barbellId: str, conversationId: str, eventType: str, content: str | JsonObject) -> ChatEvent:
        return await schema.ChatEventsRepository.create(database=self.database, userId=userId, barbellId=barbellId, conversationId=conversationId, eventType=eventType, content=content)

    async def count_user_messages_today(self, userId: str) -> int:
        startDateTime = date_util.datetime_from_now().astimezone(datetime.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        endDateTime = startDateTime + datetime.timedelta(days=1)
        query = sqlalchemy.select(sqlalchemy.func.count(schema.ChatEventsTable.c.chatEventId)).where(
            schema.ChatEventsTable.c.userId == userId,
            schema.ChatEventsTable.c.eventType == 'user',
            schema.ChatEventsTable.c.createdDate >= date_util.datetime_to_utc_naive_datetime(startDateTime),
            schema.ChatEventsTable.c.createdDate < date_util.datetime_to_utc_naive_datetime(endDateTime),
        )
        result = await self.database.execute(query=query)
        return int(result.scalar() or 0)

    async def list_events(
        self,
        userId: str,
        barbellId: str,
        conversationId: str,
        maxEvents: int = 20,
        minDate: datetime.datetime | None = None,
        shouldIncludeSteps: bool = True,
        shouldIncludePrompts: bool = True,
        shouldIncludeTools: bool = True,
    ) -> list[ChatEvent]:
        events = await schema.ChatEventsRepository.list_many(
            database=self.database,
            fieldFilters=[
                StringFieldFilter(fieldName=schema.ChatEventsTable.c.userId.key, eq=userId),
                StringFieldFilter(fieldName=schema.ChatEventsTable.c.barbellId.key, eq=barbellId),
                StringFieldFilter(fieldName=schema.ChatEventsTable.c.conversationId.key, eq=conversationId),
                *([] if shouldIncludeSteps else [StringFieldFilter(fieldName=schema.ChatEventsTable.c.eventType.key, ne='step')]),
                *([] if shouldIncludePrompts else [StringFieldFilter(fieldName=schema.ChatEventsTable.c.eventType.key, ne='prompt')]),
                *([] if shouldIncludeTools else [StringFieldFilter(fieldName=schema.ChatEventsTable.c.eventType.key, ne='tool')]),
                *([] if minDate is None else [DateFieldFilter(fieldName=schema.ChatEventsTable.c.createdDate.key, gte=minDate)]),
            ],
            orders=[
                Order(fieldName=schema.ChatEventsTable.c.createdDate.key, direction=Direction.DESCENDING),
            ],
            limit=maxEvents,
        )
        return list(reversed(events))
