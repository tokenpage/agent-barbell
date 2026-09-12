import asyncio
from typing import Any

from core.exceptions import InternalServerErrorException
from core.web3.eth_client import RestEthClient

ListAny = list[Any]  # type: ignore[explicit-any]

_RPC_SEMAPHORE = asyncio.Semaphore(10)


class ThrottledRestEthClient(RestEthClient):
    async def _make_request(self, method: str, params: ListAny | None = None) -> dict[str, Any]:  # type: ignore[explicit-any]
        async with _RPC_SEMAPHORE:
            return await super()._make_request(method=method, params=params)

    async def get_code(self, address: str, blockNumber: int | None = None) -> str:
        blockParam = hex(blockNumber) if blockNumber is not None else 'latest'
        response = await self._make_request(method='eth_getCode', params=[address, blockParam])
        return str(response.get('result', '0x'))


class EthClientManager:
    def __init__(self) -> None:
        self.ethClientsByChainId: dict[int, RestEthClient] = {}
        self.archiveEthClientsByChainId: dict[int, RestEthClient] = {}

    def register_client(self, client: RestEthClient) -> None:
        self.ethClientsByChainId[client.chainId] = client

    def register_archive_client(self, client: RestEthClient) -> None:
        self.archiveEthClientsByChainId[client.chainId] = client

    def get_archive_client(self, chainId: int) -> RestEthClient:
        if chainId not in self.archiveEthClientsByChainId:
            raise InternalServerErrorException(f'Chain {chainId} does not have an archive client')
        return self.archiveEthClientsByChainId[chainId]

    def get_regular_client(self, chainId: int) -> RestEthClient:
        if chainId in self.ethClientsByChainId:
            return self.ethClientsByChainId[chainId]
        if chainId in self.archiveEthClientsByChainId:
            return self.archiveEthClientsByChainId[chainId]
        raise InternalServerErrorException(f'Chain {chainId} does not have a regular client or an archive client')
