from core.exceptions import BadRequestException
from core.exceptions import InternalServerErrorException
from core.store.database import Database
from core.store.retriever import BooleanFieldFilter
from core.store.retriever import Direction
from core.store.retriever import Order
from core.util import chain_util
from core.web3.eth_client import ContractCall

from agent_barbell import constants
from agent_barbell.barbell_abis import AGENT_WALLET_FACTORY_ABI
from agent_barbell.barbell_abis import ERC20_ABI
from agent_barbell.eth_client_manager import EthClientManager
from agent_barbell.eth_client_manager import ThrottledRestEthClient
from agent_barbell.model import Barbell
from agent_barbell.store import schema
from agent_barbell.store.entity_repository import UUIDFieldFilter
from agent_barbell.transaction_manager import TransactionManager


class WalletManager:
    """Creates and looks up the AgentWalletKit wallet backing each barbell.

    Modelled on yieldseeker-app/api/agent_hack/create_agent_manager.py's wallet-creation path,
    collapsed to the single wallet a barbell needs.
    """

    def __init__(self, database: Database, ethClientManager: EthClientManager, transactionManager: TransactionManager) -> None:
        self.database = database
        self.ethClientManager = ethClientManager
        self.transactionManager = transactionManager

    def _get_eth_client(self, chainId: int) -> ThrottledRestEthClient:
        return self.ethClientManager.get_regular_client(chainId=chainId)

    def _get_factory_address(self, chainId: int) -> str:
        if chainId not in constants.AB_AGENT_WALLET_FACTORY_ADDRESS_MAP:
            raise BadRequestException(f'No agent wallet factory configured for chain {chainId}')
        return constants.AB_AGENT_WALLET_FACTORY_ADDRESS_MAP[chainId]


    async def calculate_wallet_address(self, chainId: int, ownerAddress: str, ownerAgentIndex: int) -> str:
        ethClient = self._get_eth_client(chainId=chainId)
        response = await ethClient.call_function_by_name(
            toAddress=self._get_factory_address(chainId=chainId),
            contractAbi=AGENT_WALLET_FACTORY_ABI,
            functionName='getAddress',
            arguments={'owner': chain_util.normalize_address(value=ownerAddress), 'ownerAgentIndex': ownerAgentIndex},
        )
        return chain_util.normalize_address(value=response[0])

    async def get_barbell(self, barbellId: str) -> Barbell:
        return await schema.BarbellsRepository.get_one(
            database=self.database,
            fieldFilters=[UUIDFieldFilter(fieldName=schema.BarbellsTable.c.barbellId.key, eq=barbellId)],
        )
    async def get_barbells_for_user(self, userId: str) -> list[Barbell]:
        return await schema.BarbellsRepository.list_many(
            database=self.database,
            fieldFilters=[UUIDFieldFilter(fieldName=schema.BarbellsTable.c.userId.key, eq=userId)],
            orders=[Order(fieldName=schema.BarbellsTable.c.createdDate.key, direction=Direction.ASCENDING)],
        )

    async def get_barbell_for_user_or_none(self, userId: str) -> Barbell | None:
        return await schema.BarbellsRepository.get_first(
            database=self.database,
            fieldFilters=[
                UUIDFieldFilter(fieldName=schema.BarbellsTable.c.userId.key, eq=userId),
                BooleanFieldFilter(fieldName=schema.BarbellsTable.c.isActive.key, eq=True),
            ],
            orders=[Order(fieldName=schema.BarbellsTable.c.createdDate.key, direction=Direction.DESCENDING)],
        )

    async def create_barbell(self, userId: str, ownerAddress: str, chainId: int, name: str, satelliteAssetAddress: str) -> Barbell:
        existingBarbell = await self.get_barbell_for_user_or_none(userId=userId)
        if existingBarbell is not None:
            if not await self.is_wallet_deployed(barbell=existingBarbell):
                await self.deploy_wallet(barbell=existingBarbell)
            return existingBarbell
        normalizedOwnerAddress = chain_util.normalize_address(value=ownerAddress)
        existingBarbells = await self.get_barbells_for_user(userId=userId)
        ownerAgentIndex = len(existingBarbells)
        walletAddress = await self.calculate_wallet_address(chainId=chainId, ownerAddress=normalizedOwnerAddress, ownerAgentIndex=ownerAgentIndex)
        barbell = await schema.BarbellsRepository.create(
            database=self.database,
            userId=userId,
            name=name,
            chainId=chainId,
            walletAddress=walletAddress,
            ownerAddress=normalizedOwnerAddress,
            anchorAssetAddress=constants.CHAIN_ANCHOR_ASSET_MAP[chainId],
            satelliteAssetAddress=satelliteAssetAddress,
            isActive=True,
        )
        await self.deploy_wallet(barbell=barbell, ownerAgentIndex=ownerAgentIndex)
        return barbell

    async def is_wallet_deployed(self, barbell: Barbell) -> bool:
        ethClient = self._get_eth_client(chainId=barbell.chainId)
        code = await ethClient.get_code(address=barbell.walletAddress)
        return len(code) > 2  # noqa: PLR2004

    async def _get_owner_agent_index(self, barbell: Barbell) -> int:
        for ownerAgentIndex, candidate in enumerate(await self.get_barbells_for_user(userId=barbell.userId)):
            if candidate.barbellId == barbell.barbellId:
                return ownerAgentIndex
        raise InternalServerErrorException(f'No owner agent index found for barbell {barbell.barbellId}')

    async def deploy_wallet(self, barbell: Barbell, ownerAgentIndex: int | None = None) -> str | None:
        if await self.is_wallet_deployed(barbell=barbell):
            return None
        if ownerAgentIndex is None:
            ownerAgentIndex = await self._get_owner_agent_index(barbell=barbell)
        transactionHash = await self.transactionManager.send_contract_transaction(
            chainId=barbell.chainId,
            toAddress=self._get_factory_address(chainId=barbell.chainId),
            contractAbi=AGENT_WALLET_FACTORY_ABI,
            functionName='createAgentWallet',
            arguments={'owner': barbell.ownerAddress, 'ownerAgentIndex': ownerAgentIndex},
        )
        if not await self.is_wallet_deployed(barbell=barbell):
            raise InternalServerErrorException(f'Wallet deployment transaction did not deploy {barbell.walletAddress}: {transactionHash}')
        return transactionHash

    async def has_barbell_holdings(self, barbell: Barbell) -> bool:
        ethClient = self._get_eth_client(chainId=barbell.chainId)
        tokenBalances = await ethClient.multicall(
            [
                ContractCall(toAddress=assetAddress, contractAbi=ERC20_ABI, functionName='balanceOf', arguments={'account': barbell.walletAddress})
                for assetAddress in [barbell.anchorAssetAddress, barbell.satelliteAssetAddress]
            ],
            shouldUseMulticall3=True,
        )
        return any(int(balance[0]) > 0 for balance in tokenBalances)

    async def deactivate_barbell(self, barbell: Barbell) -> None:
        if await self.has_barbell_holdings(barbell=barbell):
            raise BadRequestException('AGENT_HAS_BAR_BELL_HOLDINGS')
        await schema.BarbellsRepository.update(database=self.database, barbellId=barbell.barbellId, isActive=False)
