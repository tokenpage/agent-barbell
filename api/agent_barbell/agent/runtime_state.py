from pydantic import BaseModel


class RuntimeState(BaseModel):
    userId: str
    barbellId: str
    conversationId: str
