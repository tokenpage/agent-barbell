from core.api.api_request import KibaApiRequest
from core.api.authorizer import authorize_signature
from core.api.json_route import json_route
from starlette.routing import BaseRoute
from starlette.routing import Route

from agent_barbell.api import endpoints
from agent_barbell.system_manager import SystemManager


def create_v1_routes(systemManager: SystemManager) -> list[BaseRoute]:
    @json_route(requestType=endpoints.LoginRequest, responseType=endpoints.LoginResponse)
    @authorize_signature(authorizer=systemManager)
    async def login(request: KibaApiRequest[endpoints.LoginRequest]) -> endpoints.LoginResponse:
        userId = request.authBasic.username  # type: ignore[union-attr]
        user = await systemManager.get_user(userId=userId)
        return endpoints.LoginResponse(user=user)

    @json_route(requestType=endpoints.CreateUserRequest, responseType=endpoints.CreateUserResponse)
    async def create_user(request: KibaApiRequest[endpoints.CreateUserRequest]) -> endpoints.CreateUserResponse:
        user = await systemManager.create_user(
            walletAddress=request.data.walletAddress,
            username=request.data.username,
            signatureString=request.data.signatureString,
        )
        return endpoints.CreateUserResponse(user=user)

    return [
        Route('/logins', login, methods=['POST']),
        Route('/users', create_user, methods=['POST']),
    ]
