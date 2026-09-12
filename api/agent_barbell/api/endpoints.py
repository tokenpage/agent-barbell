from pydantic import BaseModel

from agent_barbell.model import User


class LoginRequest(BaseModel):
    pass


class LoginResponse(BaseModel):
    user: User


class CreateUserRequest(BaseModel):
    walletAddress: str
    username: str | None
    signatureString: str


class CreateUserResponse(BaseModel):
    user: User
