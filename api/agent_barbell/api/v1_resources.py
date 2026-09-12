import datetime

from pydantic import BaseModel

type BigInt = str


class User(BaseModel):
    userId: str
    walletAddress: str
    username: str | None


class Asset(BaseModel):
    chainId: int
    address: str
    decimals: int
    name: str
    symbol: str
    logoUri: str | None
    isAnchor: bool

class Barbell(BaseModel):
    barbellId: str
    name: str
    chainId: int
    walletAddress: str
    ownerAddress: str
    anchorAssetAddress: str
    satelliteAssetAddress: str
    isWalletDeployed: bool
    createdDate: datetime.datetime

class LegBalance(BaseModel):
    assetAddress: str
    symbol: str
    decimals: int
    balance: BigInt
    priceUsd: float
    valueUsd: float


class Portfolio(BaseModel):
    chainId: int
    walletAddress: str
    anchor: LegBalance
    satellite: LegBalance
    cash: LegBalance
    totalValueUsd: float
    satelliteBps: int


class RiskPolicy(BaseModel):
    maxDrawdownBps: int
    targetSatelliteBps: int
    maxSatelliteBps: int
    isKilled: bool
    transactionHash: str | None


class RiskState(BaseModel):
    volatility: float
    momentum: float
    peakValueUsd: float
    totalValueUsd: float
    drawdownBps: int
    currentSatelliteBps: int
    targetSatelliteBps: int
    isKillSwitchTriggered: bool
    shouldRebalance: bool
    decisionTrace: str
    policy: RiskPolicy


class RiskSnapshot(BaseModel):
    snapshotDate: datetime.datetime
    totalValueUsd: float
    satelliteBps: int
    drawdownBps: int
    volatility: float
    momentum: float
    targetSatelliteBps: int


class BarbellAction(BaseModel):
    barbellActionId: str
    createdDate: datetime.datetime
    actionType: str
    fromSatelliteBps: int
    toSatelliteBps: int
    reason: str
    decisionTrace: str
    transactionHash: str | None


class ChatMessage(BaseModel):
    chatEventId: str
    createdDate: datetime.datetime
    content: str
    isUser: bool
