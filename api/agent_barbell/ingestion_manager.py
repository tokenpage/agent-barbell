import datetime

from core import logging
from core.store.database import Database
from core.store.retriever import BooleanFieldFilter
from core.store.retriever import IntegerFieldFilter
from core.util import chain_util
from core.util import date_util

from agent_barbell import constants
from agent_barbell.barbell_abis import UNISWAP_V3_POOL_ABI
from agent_barbell.eth_client_manager import EthClientManager
from agent_barbell.eth_client_manager import ThrottledRestEthClient
from agent_barbell.model import PriceTick
from agent_barbell.portfolio_manager import PortfolioManager
from agent_barbell.store import schema

# keccak('Swap(address,address,int256,int256,uint160,uint128,int24)')
SWAP_EVENT_TOPIC = '0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67'
_WORD_LENGTH = 64
_SQRT_PRICE_WORD_INDEX = 2
_MAX_LOG_BLOCK_RANGE = 100_000


class IngestionManager:
    """Builds the price history the risk engine reasons over.

    This class is the seam between the product and its data source. Today it reads Uniswap
    `Swap` logs over RPC; Phase 3b swaps that for a Substreams pipeline writing the same
    `PriceTick` rows, and nothing downstream changes.
    """

    def __init__(self, database: Database, ethClientManager: EthClientManager, portfolioManager: PortfolioManager) -> None:
        self.database = database
        self.ethClientManager = ethClientManager
        self.portfolioManager = portfolioManager

    def _get_eth_client(self, chainId: int) -> ThrottledRestEthClient:
        return self.ethClientManager.get_regular_client(chainId=chainId)

    async def _list_tracked_asset_addresses(self, chainId: int) -> set[str]:
        barbells = await schema.BarbellsRepository.list_many(
            database=self.database,
            fieldFilters=[
                BooleanFieldFilter(fieldName=schema.BarbellsTable.c.isActive.key, eq=True),
                IntegerFieldFilter(fieldName=schema.BarbellsTable.c.chainId.key, eq=chainId),
            ],
        )
        satelliteAddresses = {barbell.satelliteAssetAddress for barbell in barbells}
        if not satelliteAddresses:
            defaultSatelliteAddress = constants.CHAIN_SATELLITE_ASSET_MAP.get(chainId)
            if defaultSatelliteAddress is not None:
                satelliteAddresses.add(defaultSatelliteAddress)
        return {constants.CHAIN_ANCHOR_ASSET_MAP[chainId], *satelliteAddresses}

    def _decode_sqrt_price_x96(self, data: str) -> int:
        payload = data.removeprefix('0x')
        start = _SQRT_PRICE_WORD_INDEX * _WORD_LENGTH
        return int(payload[start : start + _WORD_LENGTH], 16)

    def _estimate_block_date(self, blockNumber: int, latestBlockNumber: int, latestBlockDate: datetime.datetime) -> datetime.datetime:
        # NOTE: Robinhood Chain produces blocks every ~100ms, so fetching a timestamp per log
        # would mean thousands of RPC calls. Interpolating from the tip is accurate enough for a
        # volatility window measured in days.
        secondsAgo = (latestBlockNumber - blockNumber) * constants.ROBINHOOD_BLOCK_TIME_SECONDS
        return latestBlockDate - datetime.timedelta(seconds=secondsAgo)

    async def ingest_pool_price_ticks(self, chainId: int, assetAddress: str, poolAddress: str, fromBlock: int, toBlock: int) -> list[PriceTick]:
        ethClient = self._get_eth_client(chainId=chainId)
        normalizedAssetAddress = chain_util.normalize_address(value=assetAddress)
        usdgAddress = constants.CHAIN_USDG_MAP[chainId]
        token0Response = await ethClient.call_function_by_name(toAddress=poolAddress, contractAbi=UNISWAP_V3_POOL_ABI, functionName='token0', arguments={})
        token0Address = str(token0Response[0])
        asset = await self.portfolioManager.assetManager.get_asset(chainId=chainId, address=normalizedAssetAddress)
        latestBlockNumber = await ethClient.get_latest_block_number()
        latestBlockDate = date_util.datetime_from_now()
        rowDicts: list[dict[str, object]] = []
        currentFromBlock = fromBlock
        while currentFromBlock <= toBlock:
            currentToBlock = min(toBlock, currentFromBlock + _MAX_LOG_BLOCK_RANGE)
            logs = await ethClient.get_log_entries(topics=[SWAP_EVENT_TOPIC], startBlockNumber=currentFromBlock, endBlockNumber=currentToBlock, address=poolAddress)
            logging.info(f'Ingested {len(logs)} swap logs for {normalizedAssetAddress} between {currentFromBlock} and {currentToBlock}')
            for logEntry in logs:
                blockNumber = int(logEntry['blockNumber'])
                sqrtPriceX96 = self._decode_sqrt_price_x96(data=str(logEntry['data']))
                priceUsd = self.portfolioManager._price_from_slot0(  # noqa: SLF001
                    sqrtPriceX96=sqrtPriceX96,
                    token0Address=token0Address,
                    assetAddress=normalizedAssetAddress,
                    assetDecimals=asset.decimals,
                    usdgDecimals=constants.ASSET_DECIMALS_MAP[usdgAddress],
                )
                if priceUsd <= 0:
                    continue
                blockDate = self._estimate_block_date(blockNumber=blockNumber, latestBlockNumber=latestBlockNumber, latestBlockDate=latestBlockDate)
                rowDicts.append(
                    {
                        'chainId': chainId,
                        'assetAddress': normalizedAssetAddress,
                        'blockNumber': blockNumber,
                        'blockDate': blockDate,
                        'priceUsd': priceUsd,
                    }
                )
            currentFromBlock = currentToBlock + 1
        if not rowDicts:
            return []
        return await schema.PriceTicksRepository.upsert_many(
            database=self.database,
            constraintColumnNames=['chainId', 'assetAddress', 'blockNumber'],
            rowDicts=rowDicts,
        )

    async def record_spot_price_ticks(self, chainId: int) -> list[PriceTick]:
        """Sample every active barbell leg at the current block."""
        ethClient = self._get_eth_client(chainId=chainId)
        blockNumber = await ethClient.get_latest_block_number()
        anchorAddress = constants.CHAIN_ANCHOR_ASSET_MAP[chainId]
        satelliteAddresses = (await self._list_tracked_asset_addresses(chainId=chainId)) - {anchorAddress}
        pricesUsd: dict[str, float] = {}
        for satelliteAddress in sorted(satelliteAddresses):
            pricesUsd.update(await self.portfolioManager.get_leg_prices_usd(chainId=chainId, satelliteAssetAddress=satelliteAddress))
        currentDate = date_util.datetime_from_now()
        rowDicts = [{'chainId': chainId, 'assetAddress': assetAddress, 'blockNumber': blockNumber, 'blockDate': currentDate, 'priceUsd': priceUsd} for assetAddress, priceUsd in pricesUsd.items() if assetAddress != constants.CHAIN_USDG_MAP[chainId]]
        return await schema.PriceTicksRepository.upsert_many(
            database=self.database,
            constraintColumnNames=['chainId', 'assetAddress', 'blockNumber'],
            rowDicts=rowDicts,
        )

    async def backfill_recent_history(self, chainId: int, days: int = constants.VOLATILITY_WINDOW_DAYS) -> int:
        ethClient = self._get_eth_client(chainId=chainId)
        latestBlockNumber = await ethClient.get_latest_block_number()
        blocksPerDay = int((24 * 60 * 60) / constants.ROBINHOOD_BLOCK_TIME_SECONDS)
        fromBlock = max(0, latestBlockNumber - (blocksPerDay * days))
        tickCount = 0
        for assetAddress in sorted(await self._list_tracked_asset_addresses(chainId=chainId)):
            poolAddress = await self.portfolioManager.get_pool_address(chainId=chainId, assetAddress=assetAddress)
            priceTicks = await self.ingest_pool_price_ticks(chainId=chainId, assetAddress=assetAddress, poolAddress=poolAddress, fromBlock=fromBlock, toBlock=latestBlockNumber)
            tickCount += len(priceTicks)
        return tickCount

