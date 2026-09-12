from __future__ import annotations

from typing import cast

from core.exceptions import BadRequestException
from core.requester import Requester
from core.util.typing_util import JsonObject
from pydantic import BaseModel

from agent_barbell import constants


class BarbellAsset(BaseModel):
    chainId: int
    address: str
    decimals: int
    name: str
    symbol: str
    logoUri: str | None
    isAnchor: bool

class AssetManager:
    _REGISTRY_URL = 'https://api.robinhood.com/rhj/assets'

    def __init__(self, requester: Requester) -> None:
        self.requester = requester
        self._assetsByChainId: dict[int, list[BarbellAsset]] = {}
        self._registryAssets: list[JsonObject] | None = None

    async def list_supported_assets(self, chainId: int) -> list[BarbellAsset]:
        if chainId in self._assetsByChainId:
            return self._assetsByChainId[chainId]

        registryAssets = await self._list_registry_assets()
        assetsByAddress = {
            asset.address.lower(): asset
            for asset in (
                self._build_asset_from_registry(chainId=chainId, registryAsset=registryAsset)
                for registryAsset in registryAssets
                if self._has_supported_stock_deployment(registryAsset=registryAsset, chainId=chainId)
            )
        }
        anchorAddress = constants.CHAIN_ANCHOR_ASSET_MAP.get(chainId)
        if anchorAddress is not None:
            assetsByAddress[anchorAddress.lower()] = self._build_static_asset(chainId=chainId, address=anchorAddress)
        assets = sorted(assetsByAddress.values(), key=lambda asset: (asset.symbol != 'SGOV', asset.symbol))
        if not assets:
            assets = [
                self._build_static_asset(chainId=chainId, address=address)
                for address in [
                    constants.CHAIN_ANCHOR_ASSET_MAP.get(chainId),
                    *constants.CHAIN_SATELLITE_ASSET_OPTIONS_MAP.get(chainId, ()),
                ]
                if address is not None
            ]
        self._assetsByChainId[chainId] = assets
        return assets

    async def get_asset(self, chainId: int, address: str) -> BarbellAsset:
        normalizedAddress = address.lower()
        if normalizedAddress == constants.CHAIN_USDG_MAP.get(chainId, '').lower():
            return self._build_static_asset(chainId=chainId, address=constants.CHAIN_USDG_MAP[chainId])
        if normalizedAddress == constants.CHAIN_WETH_MAP.get(chainId, '').lower():
            return self._build_static_asset(chainId=chainId, address=constants.CHAIN_WETH_MAP[chainId])
        asset = next((candidate for candidate in await self.list_supported_assets(chainId=chainId) if candidate.address.lower() == normalizedAddress), None)
        if asset is None:
            raise BadRequestException(f'Unsupported asset for chain {chainId}: {address}')
        return asset

    async def get_assets(self, chainId: int, addresses: list[str]) -> list[BarbellAsset]:
        return [await self.get_asset(chainId=chainId, address=address) for address in addresses]

    async def resolve_satellite_asset_address(self, chainId: int, address: str) -> str:
        asset = await self.get_asset(chainId=chainId, address=address)
        anchorAddress = constants.CHAIN_ANCHOR_ASSET_MAP.get(chainId)
        if anchorAddress is not None and asset.address.lower() == anchorAddress.lower():
            raise BadRequestException(f'Anchor asset cannot be selected as satellite asset: {address}')
        return asset.address

    async def _list_registry_assets(self) -> list[JsonObject]:
        if self._registryAssets is not None:
            return self._registryAssets
        try:
            response = await self.requester.get(url=self._REGISTRY_URL)
            payload = cast(JsonObject, response.json())
        except Exception:
            self._registryAssets = []
            return self._registryAssets
        rawAssets = payload.get('assets')
        if not isinstance(rawAssets, list):
            self._registryAssets = []
            return self._registryAssets
        self._registryAssets = [cast(JsonObject, rawAsset) for rawAsset in rawAssets if isinstance(rawAsset, dict)]
        return self._registryAssets

    def _has_supported_stock_deployment(self, registryAsset: JsonObject, chainId: int) -> bool:
        if registryAsset.get('status') not in {None, 'ASSET_STATUS_ACTIVE'}:
            return False
        if not registryAsset.get('isin'):
            return False
        return self._get_deployment(registryAsset=registryAsset, chainId=chainId) is not None

    def _build_asset_from_registry(self, chainId: int, registryAsset: JsonObject) -> BarbellAsset:
        deployment = self._get_deployment(registryAsset=registryAsset, chainId=chainId)
        if deployment is None:
            raise BadRequestException(f'Registry asset has no deployment for chain {chainId}')
        address = str(deployment['contractAddress'])
        fallbackSymbol = constants.ASSET_SYMBOL_MAP.get(address, str(registryAsset.get('tokenSymbol') or address[:8]))
        fallbackName = constants.ASSET_NAME_MAP.get(address, fallbackSymbol)
        tokenName = str(registryAsset.get('tokenName') or fallbackName)
        return BarbellAsset(
            chainId=chainId,
            address=address,
            decimals=int(registryAsset.get('tokenDecimals') or constants.ASSET_DECIMALS_MAP.get(address, 18)),
            name=tokenName.removesuffix(' • Robinhood Token'),
            symbol=str(registryAsset.get('tokenSymbol') or fallbackSymbol),
            logoUri=str(registryAsset['logoUrl']) if registryAsset.get('logoUrl') else f'https://cdn.robinhood.com/ncw_assets/logos/{address.lower()}.png',
            isAnchor=address.lower() == constants.CHAIN_ANCHOR_ASSET_MAP.get(chainId, '').lower(),
        )

    def _build_static_asset(self, chainId: int, address: str) -> BarbellAsset:
        symbol = constants.ASSET_SYMBOL_MAP.get(address, address[:8])
        return BarbellAsset(
            chainId=chainId,
            address=address,
            decimals=constants.ASSET_DECIMALS_MAP[address],
            name=constants.ASSET_NAME_MAP.get(address, symbol),
            symbol=symbol,
            logoUri=f'https://cdn.robinhood.com/ncw_assets/logos/{address.lower()}.png',
            isAnchor=address.lower() == constants.CHAIN_ANCHOR_ASSET_MAP.get(chainId, '').lower(),
        )

    def _get_deployment(self, registryAsset: JsonObject, chainId: int) -> JsonObject | None:
        deployments = registryAsset.get('deployments')
        if not isinstance(deployments, list):
            return None
        return next(
            (
                cast(JsonObject, deployment)
                for deployment in deployments
                if isinstance(deployment, dict)
                and int(deployment.get('chainId') or 0) == chainId
                and deployment.get('contractAddress')
            ),
            None,
        )
