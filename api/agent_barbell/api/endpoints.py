from pydantic import BaseModel
from pydantic import Field

from agent_barbell import constants
from agent_barbell.api import v1_resources as resources


class LoginRequest(BaseModel):
    pass


class LoginResponse(BaseModel):
    user: resources.User


class CreateUserRequest(BaseModel):
    walletAddress: str
    username: str | None
    signatureString: str


class CreateUserResponse(BaseModel):
    user: resources.User


class BarbellCreationDraft(BaseModel):
    name: str = Field(max_length=constants.BARBELL_NAME_MAX_LENGTH)
    satelliteAssetAddress: str
    maxDrawdownBps: int = Field(ge=0, le=constants.MAX_BPS)
    targetSatelliteBps: int = Field(ge=0, le=constants.MAX_BPS)
    maxSatelliteBps: int = Field(ge=0, le=constants.MAX_BPS)


class CreateBarbellRequest(BarbellCreationDraft):
    pass


class CreateBarbellResponse(BaseModel):
    barbell: resources.Barbell

class ListBarbellAssetsRequest(BaseModel):
    pass

class ListBarbellAssetsResponse(BaseModel):
    assets: list[resources.Asset]


class DeactivateBarbellRequest(BaseModel):
    pass


class DeactivateBarbellResponse(BaseModel):
    deactivated: bool


class GetBarbellRequest(BaseModel):
    pass


class GetBarbellResponse(BaseModel):
    barbell: resources.Barbell | None


class GetBarbellPortfolioRequest(BaseModel):
    pass


class GetBarbellPortfolioResponse(BaseModel):
    portfolio: resources.Portfolio


class GetBarbellRiskStateRequest(BaseModel):
    pass


class GetBarbellRiskStateResponse(BaseModel):
    riskState: resources.RiskState


class ListBarbellSnapshotsRequest(BaseModel):
    pass


class ListBarbellSnapshotsResponse(BaseModel):
    snapshots: list[resources.RiskSnapshot]


class ListBarbellActionsRequest(BaseModel):
    pass


class ListBarbellActionsResponse(BaseModel):
    actions: list[resources.BarbellAction]


class SetRiskBudgetRequest(BaseModel):
    maxDrawdownBps: int
    targetSatelliteBps: int
    maxSatelliteBps: int


class SetRiskBudgetResponse(BaseModel):
    riskState: resources.RiskState


class ListChatMessagesRequest(BaseModel):
    pass


class ListChatMessagesResponse(BaseModel):
    messages: list[resources.ChatMessage]


class AddUserMessageStreamedRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class AddCreationMessageStreamedRequest(BarbellCreationDraft):
    content: str = Field(min_length=1, max_length=2000)


class AddUserMessageStreamedResponse(BaseModel):
    message: resources.ChatMessage
