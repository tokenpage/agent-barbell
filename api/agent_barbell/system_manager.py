import base64
import datetime

from core.api.authorizer import SignatureAuthorizer
from core.exceptions import BadRequestException
from core.exceptions import ForbiddenException
from core.exceptions import NotFoundException
from core.exceptions import UnauthorizedException
from core.requester import Requester
from core.util import chain_util
from core.util import date_util
from eth_account.messages import encode_defunct
from siwe import SiweMessage  # type: ignore[import-untyped]
from web3 import Web3

from agent_barbell import constants
from agent_barbell.asset_manager import AssetManager
from agent_barbell.conversation_manager import ConversationManager
from agent_barbell.eth_client_manager import EthClientManager
from agent_barbell.ingestion_manager import IngestionManager
from agent_barbell.model import AuthToken
from agent_barbell.model import Barbell
from agent_barbell.model import BarbellAction
from agent_barbell.model import User
from agent_barbell.portfolio_manager import Portfolio
from agent_barbell.portfolio_manager import PortfolioManager
from agent_barbell.risk_engine import RiskState
from agent_barbell.risk_manager import RiskManager
from agent_barbell.store import schema
from agent_barbell.store.entity_repository import UUIDFieldFilter
from agent_barbell.user_manager import UserManager
from agent_barbell.wallet_manager import WalletManager

w3 = Web3()


class SystemManager(SignatureAuthorizer):
    def __init__(
        self,
        requester: Requester,
        ethClientManager: EthClientManager,
        assetManager: AssetManager,
        userManager: UserManager,
        walletManager: WalletManager,
        portfolioManager: PortfolioManager,
        riskManager: RiskManager,
        ingestionManager: IngestionManager,
        conversationManager: ConversationManager,
        appUrl: str,
        authExtraAllowedDomains: set[str] | None = None,
    ) -> None:
        self.ethClientManager = ethClientManager
        self.requester = requester
        self.assetManager = assetManager
        self.userManager = userManager
        self.walletManager = walletManager
        self.portfolioManager = portfolioManager
        self.riskManager = riskManager
        self.ingestionManager = ingestionManager
        self.conversationManager = conversationManager
        self.appUrl = appUrl
        self.authAllowedDomains = {domain.lower().split('://', 1)[-1] for domain in {*constants.AUTH_SIGNATURE_ALLOWED_DOMAINS, *(authExtraAllowedDomains or set())}}
        self._signatureSignerMap: dict[str, str] = {}

    def _verify_signature_claims(self, siweMessage: SiweMessage) -> None:
        normalizedDomain = (siweMessage.domain or '').lower().split('://', 1)[-1]
        if normalizedDomain not in self.authAllowedDomains:
            raise UnauthorizedException('AUTH_DOMAIN_INVALID')
        now = date_util.datetime_from_now()
        if siweMessage.expiration_time is not None and datetime.datetime.fromisoformat(str(siweMessage.expiration_time)) < now:
            raise UnauthorizedException('AUTH_SIGNATURE_EXPIRED')
        if datetime.datetime.fromisoformat(str(siweMessage.issued_at)) < date_util.datetime_from_now(days=-constants.AUTH_SIGNATURE_MAX_AGE_DAYS):
            raise UnauthorizedException('AUTH_SIGNATURE_EXPIRED')

    async def retrieve_signature_signer_address(self, signatureString: str) -> str:
        authTokenJson = base64.b64decode(signatureString).decode('utf-8')
        authToken = AuthToken.model_validate_json(authTokenJson)
        siweMessage = SiweMessage.from_message(message=authToken.message)
        self._verify_signature_claims(siweMessage=siweMessage)
        if signatureString in self._signatureSignerMap:
            return self._signatureSignerMap[signatureString]
        messageHash = encode_defunct(text=authToken.message)
        signerId = chain_util.normalize_address(siweMessage.address)
        messageSignerId = chain_util.normalize_address(w3.eth.account.recover_message(messageHash, signature=authToken.signature))
        if messageSignerId != signerId:
            raise UnauthorizedException('AUTH_SIGNATURE_INVALID')
        self._signatureSignerMap[signatureString] = signerId
        return signerId

    async def retrieve_signature_signer(self, signatureString: str) -> str:
        signerAddress = await self.retrieve_signature_signer_address(signatureString=signatureString)
        user = await self._get_user_by_wallet_address(walletAddress=signerAddress)
        return user.userId

    async def _get_user_by_wallet_address(self, walletAddress: str) -> User:
        try:
            user = await self.userManager.get_user_by_wallet_address(walletAddress=walletAddress)
        except NotFoundException:
            raise UnauthorizedException('NO_USER')
        return user

    async def get_user(self, userId: str) -> User:
        return await self.userManager.get_user(userId=userId)

    async def user_login_with_wallet_address(self, walletAddress: str, userId: str) -> User:
        user = await self._get_user_by_wallet_address(walletAddress=walletAddress)
        if user.userId != userId:
            raise ForbiddenException('INCORRECT_USER')
        return user

    async def create_user(self, walletAddress: str, username: str | None, signatureString: str) -> User:
        signerAddress = await self.retrieve_signature_signer_address(signatureString=signatureString)
        if signerAddress != chain_util.normalize_address(walletAddress):
            raise UnauthorizedException('AUTH_SIGNATURE_INVALID')
        existingUser = await self.userManager.get_user_by_wallet_address_or_none(walletAddress=signerAddress)
        if existingUser is not None:
            return existingUser
        return await self.userManager.create_user(walletAddress=signerAddress, username=username)

    @staticmethod
    def _validate_barbell_name(name: str) -> str:
        normalizedName = name.strip()
        if len(normalizedName) < constants.BARBELL_NAME_MIN_LENGTH:
            raise BadRequestException('BARBELL_NAME_TOO_SHORT')
        if len(normalizedName) > constants.BARBELL_NAME_MAX_LENGTH:
            raise BadRequestException('BARBELL_NAME_TOO_LONG')
        if any(character not in constants.BARBELL_NAME_ALLOWED_CHARACTERS for character in normalizedName):
            raise BadRequestException('BARBELL_NAME_INVALID')
        return normalizedName

    @staticmethod
    def _validate_creation_risk_budget(maxDrawdownBps: int, targetSatelliteBps: int, maxSatelliteBps: int) -> None:
        if not constants.MIN_MAX_DRAWDOWN_BPS <= maxDrawdownBps <= constants.MAX_MAX_DRAWDOWN_BPS:
            raise BadRequestException('MAX_DRAWDOWN_OUT_OF_RANGE')
        if not 0 <= maxSatelliteBps <= constants.MAX_BPS:
            raise BadRequestException('MAX_SATELLITE_OUT_OF_RANGE')
        if not 0 <= targetSatelliteBps <= maxSatelliteBps:
            raise BadRequestException('TARGET_SATELLITE_OUT_OF_RANGE')

    async def create_barbell(
        self,
        userId: str,
        name: str,
        satelliteAssetAddress: str,
        maxDrawdownBps: int,
        targetSatelliteBps: int,
        maxSatelliteBps: int,
    ) -> Barbell:
        user = await self.userManager.get_user(userId=userId)
        normalizedName = self._validate_barbell_name(name=name)
        self._validate_creation_risk_budget(
            maxDrawdownBps=maxDrawdownBps,
            targetSatelliteBps=targetSatelliteBps,
            maxSatelliteBps=maxSatelliteBps,
        )
        normalizedSatelliteAssetAddress = await self.assetManager.resolve_satellite_asset_address(
            chainId=constants.ROBINHOOD_CHAIN_ID,
            address=satelliteAssetAddress,
        )
        await self.portfolioManager.get_pool_address(
            chainId=constants.ROBINHOOD_CHAIN_ID,
            assetAddress=normalizedSatelliteAssetAddress,
        )
        existingBarbell = await self.walletManager.get_barbell_for_user_or_none(userId=userId)
        barbell = await self.walletManager.create_barbell(
            userId=userId,
            ownerAddress=user.walletAddress,
            chainId=constants.ROBINHOOD_CHAIN_ID,
            name=normalizedName,
            satelliteAssetAddress=normalizedSatelliteAssetAddress,
        )
        if existingBarbell is None:
            await self.riskManager.set_policy(
                barbellId=barbell.barbellId,
                maxDrawdownBps=maxDrawdownBps,
                targetSatelliteBps=targetSatelliteBps,
                maxSatelliteBps=maxSatelliteBps,
            )
        return barbell

    async def get_portfolio(self, barbell: Barbell) -> Portfolio:
        return await self.portfolioManager.get_portfolio(barbell=barbell)

    async def get_risk_state(self, barbell: Barbell) -> RiskState:
        return await self.riskManager.get_risk_state(barbell=barbell)

    async def set_risk_budget(self, barbell: Barbell, maxDrawdownBps: int, targetSatelliteBps: int, maxSatelliteBps: int) -> None:
        await self.riskManager.set_policy(
            barbellId=barbell.barbellId,
            maxDrawdownBps=maxDrawdownBps,
            targetSatelliteBps=targetSatelliteBps,
            maxSatelliteBps=maxSatelliteBps,
        )

    async def publish_policy_onchain(self, barbell: Barbell) -> str:
        """Write the policy to RiskBudgetRegistry so the promise is publicly verifiable.

        Deliberately not called by set_risk_budget: the persisted policy already drives the
        engine, so the product works without it, and this is the only part that needs a
        transaction.
        """
        raise NotImplementedError(f'setPolicy({barbell.walletAddress}) on RiskBudgetRegistry needs TransactionManager (Phase 5). The policy is already persisted and drives the engine; only the public on-chain record is missing.')

    async def list_barbell_actions(self, barbellId: str) -> list[BarbellAction]:
        return await schema.BarbellActionsRepository.list_many(
            database=self.userManager.database,
            fieldFilters=[UUIDFieldFilter(fieldName=schema.BarbellActionsTable.c.barbellId.key, eq=barbellId)],
        )
