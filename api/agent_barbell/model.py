import datetime

from core.util.typing_util import JsonObject
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


class Barbell(BaseModel):
    barbellId: str
    name: str
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    userId: str
    chainId: int
    walletAddress: str
    ownerAddress: str
    anchorAssetAddress: str
    satelliteAssetAddress: str
    isActive: bool


class BarbellPolicy(BaseModel):
    barbellPolicyId: str
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    barbellId: str
    maxDrawdownBps: int
    targetSatelliteBps: int
    maxSatelliteBps: int
    isKilled: bool
    transactionHash: str | None


class PriceTick(BaseModel):
    priceTickId: str
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    chainId: int
    assetAddress: str
    blockNumber: int
    blockDate: datetime.datetime
    priceUsd: float


class RiskSnapshot(BaseModel):
    riskSnapshotId: str
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    barbellId: str
    snapshotDate: datetime.datetime
    totalValueUsd: float
    anchorValueUsd: float
    satelliteValueUsd: float
    cashValueUsd: float
    satelliteBps: int
    peakValueUsd: float
    drawdownBps: int
    volatility: float
    momentum: float
    targetSatelliteBps: int


class BarbellAction(BaseModel):
    barbellActionId: str
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    barbellId: str
    actionType: str
    fromSatelliteBps: int
    toSatelliteBps: int
    reason: str
    decisionTrace: str
    transactionHash: str | None


class ChatEvent(BaseModel):
    chatEventId: str
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    userId: str
    barbellId: str
    conversationId: str
    eventType: str
    content: str | JsonObject
