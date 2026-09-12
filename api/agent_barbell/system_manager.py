import base64
import datetime

from core.api.authorizer import SignatureAuthorizer
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
from agent_barbell.eth_client_manager import EthClientManager
from agent_barbell.model import AuthToken
from agent_barbell.model import User
from agent_barbell.user_manager import UserManager

w3 = Web3()


class SystemManager(SignatureAuthorizer):
    def __init__(
        self,
        requester: Requester,
        ethClientManager: EthClientManager,
        userManager: UserManager,
        appUrl: str,
        authExtraAllowedDomains: set[str] | None = None,
    ) -> None:
        self.requester = requester
        self.ethClientManager = ethClientManager
        self.userManager = userManager
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
