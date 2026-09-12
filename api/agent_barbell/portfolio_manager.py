import math

from core.exceptions import BadRequestException
from core.util import chain_util
from core.web3.eth_client import ContractCall
from pydantic import BaseModel

from agent_barbell import constants
from agent_barbell.asset_manager import AssetManager
from agent_barbell.barbell_abis import ERC20_ABI
from agent_barbell.barbell_abis import UNISWAP_V3_FACTORY_ABI
from agent_barbell.barbell_abis import UNISWAP_V3_POOL_ABI
from agent_barbell.eth_client_manager import EthClientManager
from agent_barbell.eth_client_manager import ThrottledRestEthClient
from agent_barbell.model import Barbell

_Q96 = 2**96
_POOL_FEE_TIERS = (100, 500, 3000, 10000)
_ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'


class LegBalance(BaseModel):
    assetAddress: str
    symbol: str
    decimals: int
    balance: int
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


class PortfolioManager:
    """Reads barbell balances and prices every configured stock against USDG."""

    def __init__(self, ethClientManager: EthClientManager, assetManager: AssetManager) -> None:
        self.ethClientManager = ethClientManager
        self.assetManager = assetManager
        self._poolAddressByAsset: dict[tuple[int, str], str] = {}

    def _get_eth_client(self, chainId: int) -> ThrottledRestEthClient:
        return self.ethClientManager.get_regular_client(chainId=chainId)

    def _price_from_slot0(self, sqrtPriceX96: int, token0Address: str, assetAddress: str, assetDecimals: int, usdgDecimals: int) -> float:
        ratio = float((sqrtPriceX96 / _Q96) ** 2)
        if chain_util.normalize_address(value=token0Address) == chain_util.normalize_address(value=assetAddress):
            return ratio * float(10 ** (assetDecimals - usdgDecimals))
        if ratio == 0:
            return 0.0
        return (1 / ratio) * float(10 ** (assetDecimals - usdgDecimals))

    async def get_pool_address(self, chainId: int, assetAddress: str) -> str:
        normalizedAssetAddress = chain_util.normalize_address(value=assetAddress)
        cacheKey = (chainId, normalizedAssetAddress.lower())
        if cacheKey in self._poolAddressByAsset:
            return self._poolAddressByAsset[cacheKey]
        anchorAddress = constants.CHAIN_ANCHOR_ASSET_MAP.get(chainId)
        knownSatelliteAddress = constants.CHAIN_SATELLITE_ASSET_MAP.get(chainId)
        if anchorAddress is not None and normalizedAssetAddress.lower() == anchorAddress.lower():
            poolAddress = constants.ANCHOR_POOL_ADDRESS_MAP[chainId]
        elif knownSatelliteAddress is not None and normalizedAssetAddress.lower() == knownSatelliteAddress.lower():
            poolAddress = constants.SATELLITE_POOL_ADDRESS_MAP[chainId]
        else:
            poolAddress = await self._discover_pool_address(chainId=chainId, assetAddress=normalizedAssetAddress)
        self._poolAddressByAsset[cacheKey] = poolAddress
        return poolAddress

    async def _discover_pool_address(self, chainId: int, assetAddress: str) -> str:
        factoryAddress = constants.UNISWAP_V3_FACTORY_ADDRESS_MAP.get(chainId)
        if factoryAddress is None:
            raise BadRequestException(f'No Uniswap V3 factory configured for chain {chainId}')
        usdgAddress = constants.CHAIN_USDG_MAP[chainId]
        ethClient = self._get_eth_client(chainId=chainId)
        poolResponses = await ethClient.multicall(
            [
                ContractCall(
                    toAddress=factoryAddress,
                    contractAbi=UNISWAP_V3_FACTORY_ABI,
                    functionName='getPool',
                    arguments={'tokenA': assetAddress, 'tokenB': usdgAddress, 'fee': feeTier},
                )
                for feeTier in _POOL_FEE_TIERS
            ],
            shouldUseMulticall3=True,
        )
        poolAddresses = [str(response[0]) for response in poolResponses if str(response[0]).lower() != _ZERO_ADDRESS.lower()]
        if not poolAddresses:
            raise BadRequestException(f'No USDG liquidity pool configured for asset {assetAddress}')
        liquidityResponses = await ethClient.multicall(
            [ContractCall(toAddress=poolAddress, contractAbi=UNISWAP_V3_POOL_ABI, functionName='liquidity', arguments={}) for poolAddress in poolAddresses],
            shouldUseMulticall3=True,
        )
        poolAddress, liquidity = max(zip(poolAddresses, liquidityResponses, strict=True), key=lambda item: int(item[1][0]))
        if int(liquidity[0]) <= 0:
            raise BadRequestException(f'USDG liquidity pool has no liquidity for asset {assetAddress}')
        return poolAddress

    async def _get_leg_price_usd(self, chainId: int, assetAddress: str, poolAddress: str, assetDecimals: int) -> float:
        ethClient = self._get_eth_client(chainId=chainId)
        usdgAddress = constants.CHAIN_USDG_MAP[chainId]
        slot0Response, token0Response = await ethClient.multicall(
            [
                ContractCall(toAddress=poolAddress, contractAbi=UNISWAP_V3_POOL_ABI, functionName='slot0', arguments={}),
                ContractCall(toAddress=poolAddress, contractAbi=UNISWAP_V3_POOL_ABI, functionName='token0', arguments={}),
            ],
            shouldUseMulticall3=True,
        )
        return self._price_from_slot0(
            sqrtPriceX96=int(slot0Response[0]),
            token0Address=str(token0Response[0]),
            assetAddress=assetAddress,
            assetDecimals=assetDecimals,
            usdgDecimals=constants.ASSET_DECIMALS_MAP[usdgAddress],
        )

    async def get_leg_prices_usd(self, chainId: int, satelliteAssetAddress: str | None = None) -> dict[str, float]:
        anchorAddress = constants.CHAIN_ANCHOR_ASSET_MAP[chainId]
        satelliteAddress = satelliteAssetAddress or constants.CHAIN_SATELLITE_ASSET_MAP[chainId]
        anchorAsset, satelliteAsset = await self.assetManager.get_assets(chainId=chainId, addresses=[anchorAddress, satelliteAddress])
        anchorPrice = await self._get_leg_price_usd(
            chainId=chainId,
            assetAddress=anchorAddress,
            poolAddress=await self.get_pool_address(chainId=chainId, assetAddress=anchorAddress),
            assetDecimals=anchorAsset.decimals,
        )
        satellitePrice = await self._get_leg_price_usd(
            chainId=chainId,
            assetAddress=satelliteAddress,
            poolAddress=await self.get_pool_address(chainId=chainId, assetAddress=satelliteAddress),
            assetDecimals=satelliteAsset.decimals,
        )
        return {
            anchorAddress: anchorPrice,
            satelliteAddress: satellitePrice,
            constants.CHAIN_USDG_MAP[chainId]: 1.0,
        }

    async def get_portfolio(self, barbell: Barbell) -> Portfolio:
        chainId = barbell.chainId
        ethClient = self._get_eth_client(chainId=chainId)
        usdgAddress = constants.CHAIN_USDG_MAP[chainId]
        assetAddresses = [barbell.anchorAssetAddress, barbell.satelliteAssetAddress, usdgAddress]
        balanceResponses = await ethClient.multicall(
            [ContractCall(toAddress=assetAddress, contractAbi=ERC20_ABI, functionName='balanceOf', arguments={'account': barbell.walletAddress}) for assetAddress in assetAddresses],
            shouldUseMulticall3=True,
        )
        assets = await self.assetManager.get_assets(chainId=chainId, addresses=assetAddresses)
        pricesUsd = await self.get_leg_prices_usd(chainId=chainId, satelliteAssetAddress=barbell.satelliteAssetAddress)
        legs: list[LegBalance] = []
        for asset, balanceResponse in zip(assets, balanceResponses, strict=True):
            balance = int(balanceResponse[0])
            priceUsd = pricesUsd[asset.address]
            legs.append(
                LegBalance(
                    assetAddress=asset.address,
                    symbol=asset.symbol,
                    decimals=asset.decimals,
                    balance=balance,
                    priceUsd=priceUsd,
                    valueUsd=(balance / (10**asset.decimals)) * priceUsd,
                )
            )
        anchor, satellite, cash = legs
        totalValueUsd = anchor.valueUsd + satellite.valueUsd + cash.valueUsd
        satelliteBps = 0 if totalValueUsd <= 0 else min(constants.MAX_BPS, math.floor((satellite.valueUsd / totalValueUsd) * constants.MAX_BPS))
        return Portfolio(
            chainId=chainId,
            walletAddress=barbell.walletAddress,
            anchor=anchor,
            satellite=satellite,
            cash=cash,
            totalValueUsd=totalValueUsd,
            satelliteBps=satelliteBps,
        )
