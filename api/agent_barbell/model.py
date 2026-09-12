import datetime

from pydantic import BaseModel


class User(BaseModel):
    userId: str
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    walletAddress: str
    username: str | None


class AuthToken(BaseModel):
    message: str
    signature: str
