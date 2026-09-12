import typing

from core.api.api_request import KibaApiRequest
from core.api.authorizer import authorize_signature
from core.api.json_route import json_route
from core.api.streaming_json_route import streaming_json_route
from core.exceptions import ForbiddenException
from starlette.routing import BaseRoute
from starlette.routing import Route

from agent_barbell.api import v1_resources as resources
from agent_barbell.api import endpoints
from agent_barbell.api.v1_resource_builder import ResourceBuilderV1
from agent_barbell.model import Barbell
from agent_barbell.system_manager import SystemManager


def create_v1_routes(systemManager: SystemManager, resourceBuilder: ResourceBuilderV1) -> list[BaseRoute]:
    async def _get_authorized_barbell(userId: str, barbellId: str) -> Barbell:
        barbell = await systemManager.walletManager.get_barbell(barbellId=barbellId)
        if barbell.userId != userId:
            raise ForbiddenException('INCORRECT_USER')
        return barbell

    @json_route(requestType=endpoints.LoginRequest, responseType=endpoints.LoginResponse)
    @authorize_signature(authorizer=systemManager)
    async def login(request: KibaApiRequest[endpoints.LoginRequest]) -> endpoints.LoginResponse:
        userId = request.authBasic.username  # type: ignore[union-attr]
        user = await systemManager.get_user(userId=userId)
        return endpoints.LoginResponse(user=resourceBuilder.user_from_model(user=user))

    @json_route(requestType=endpoints.CreateUserRequest, responseType=endpoints.CreateUserResponse)
    async def create_user(request: KibaApiRequest[endpoints.CreateUserRequest]) -> endpoints.CreateUserResponse:
        user = await systemManager.create_user(
            walletAddress=request.data.walletAddress,
            username=request.data.username,
            signatureString=request.data.signatureString,
        )
        return endpoints.CreateUserResponse(user=resourceBuilder.user_from_model(user=user))

    @json_route(requestType=endpoints.ListBarbellAssetsRequest, responseType=endpoints.ListBarbellAssetsResponse)
    async def list_barbell_assets(request: KibaApiRequest[endpoints.ListBarbellAssetsRequest]) -> endpoints.ListBarbellAssetsResponse:
        assets = await systemManager.assetManager.list_supported_assets(chainId=int(request.path_params['chainId']))
        return endpoints.ListBarbellAssetsResponse(
            assets=[
                resources.Asset(
                    chainId=asset.chainId,
                    address=asset.address,
                    decimals=asset.decimals,
                    name=asset.name,
                    symbol=asset.symbol,
                    logoUri=asset.logoUri,
                    isAnchor=asset.isAnchor,
                )
                for asset in assets
            ],
        )

    @json_route(requestType=endpoints.GetBarbellRequest, responseType=endpoints.GetBarbellResponse)
    @authorize_signature(authorizer=systemManager)
    async def get_barbell(request: KibaApiRequest[endpoints.GetBarbellRequest]) -> endpoints.GetBarbellResponse:
        userId = request.authBasic.username  # type: ignore[union-attr]
        barbell = await systemManager.walletManager.get_barbell_for_user_or_none(userId=userId)
        if barbell is None:
            return endpoints.GetBarbellResponse(barbell=None)
        return endpoints.GetBarbellResponse(barbell=await resourceBuilder.barbell_from_model(barbell=barbell))

    @json_route(requestType=endpoints.CreateBarbellRequest, responseType=endpoints.CreateBarbellResponse)
    @authorize_signature(authorizer=systemManager)
    async def create_barbell(request: KibaApiRequest[endpoints.CreateBarbellRequest]) -> endpoints.CreateBarbellResponse:
        userId = request.authBasic.username  # type: ignore[union-attr]
        barbell = await systemManager.create_barbell(
            userId=userId,
            name=request.data.name,
            satelliteAssetAddress=request.data.satelliteAssetAddress,
            maxDrawdownBps=request.data.maxDrawdownBps,
            targetSatelliteBps=request.data.targetSatelliteBps,
            maxSatelliteBps=request.data.maxSatelliteBps,
        )
        return endpoints.CreateBarbellResponse(barbell=await resourceBuilder.barbell_from_model(barbell=barbell))

    @json_route(requestType=endpoints.DeactivateBarbellRequest, responseType=endpoints.DeactivateBarbellResponse)
    @authorize_signature(authorizer=systemManager)
    async def deactivate_barbell(request: KibaApiRequest[endpoints.DeactivateBarbellRequest]) -> endpoints.DeactivateBarbellResponse:
        userId = request.authBasic.username  # type: ignore[union-attr]
        barbell = await _get_authorized_barbell(userId=userId, barbellId=request.path_params['barbellId'])
        await systemManager.walletManager.deactivate_barbell(barbell=barbell)
        return endpoints.DeactivateBarbellResponse(deactivated=True)


    @json_route(requestType=endpoints.GetBarbellPortfolioRequest, responseType=endpoints.GetBarbellPortfolioResponse)
    @authorize_signature(authorizer=systemManager)
    async def get_barbell_portfolio(request: KibaApiRequest[endpoints.GetBarbellPortfolioRequest]) -> endpoints.GetBarbellPortfolioResponse:
        userId = request.authBasic.username  # type: ignore[union-attr]
        barbell = await _get_authorized_barbell(userId=userId, barbellId=request.path_params['barbellId'])
        portfolio = await systemManager.portfolioManager.get_portfolio(barbell=barbell)
        return endpoints.GetBarbellPortfolioResponse(portfolio=resourceBuilder.portfolio_from_model(portfolio=portfolio))

    @json_route(requestType=endpoints.GetBarbellRiskStateRequest, responseType=endpoints.GetBarbellRiskStateResponse)
    @authorize_signature(authorizer=systemManager)
    async def get_barbell_risk_state(request: KibaApiRequest[endpoints.GetBarbellRiskStateRequest]) -> endpoints.GetBarbellRiskStateResponse:
        userId = request.authBasic.username  # type: ignore[union-attr]
        barbell = await _get_authorized_barbell(userId=userId, barbellId=request.path_params['barbellId'])
        riskState = await systemManager.get_risk_state(barbell=barbell)
        policy = await resourceBuilder.policy_resource(barbellId=barbell.barbellId)
        return endpoints.GetBarbellRiskStateResponse(riskState=resourceBuilder.risk_state_from_model(riskState=riskState, policy=policy))

    @json_route(requestType=endpoints.SetRiskBudgetRequest, responseType=endpoints.SetRiskBudgetResponse)
    @authorize_signature(authorizer=systemManager)
    async def set_risk_budget(request: KibaApiRequest[endpoints.SetRiskBudgetRequest]) -> endpoints.SetRiskBudgetResponse:
        userId = request.authBasic.username  # type: ignore[union-attr]
        barbell = await _get_authorized_barbell(userId=userId, barbellId=request.path_params['barbellId'])
        await systemManager.set_risk_budget(
            barbell=barbell,
            maxDrawdownBps=request.data.maxDrawdownBps,
            targetSatelliteBps=request.data.targetSatelliteBps,
            maxSatelliteBps=request.data.maxSatelliteBps,
        )
        riskState = await systemManager.get_risk_state(barbell=barbell)
        policy = await resourceBuilder.policy_resource(barbellId=barbell.barbellId)
        return endpoints.SetRiskBudgetResponse(riskState=resourceBuilder.risk_state_from_model(riskState=riskState, policy=policy))

    @json_route(requestType=endpoints.ListBarbellSnapshotsRequest, responseType=endpoints.ListBarbellSnapshotsResponse)
    @authorize_signature(authorizer=systemManager)
    async def list_barbell_snapshots(request: KibaApiRequest[endpoints.ListBarbellSnapshotsRequest]) -> endpoints.ListBarbellSnapshotsResponse:
        userId = request.authBasic.username  # type: ignore[union-attr]
        barbell = await _get_authorized_barbell(userId=userId, barbellId=request.path_params['barbellId'])
        snapshots = await systemManager.riskManager.list_snapshots(barbellId=barbell.barbellId)
        return endpoints.ListBarbellSnapshotsResponse(snapshots=[resourceBuilder.snapshot_from_model(snapshot=snapshot) for snapshot in snapshots])

    @json_route(requestType=endpoints.ListBarbellActionsRequest, responseType=endpoints.ListBarbellActionsResponse)
    @authorize_signature(authorizer=systemManager)
    async def list_barbell_actions(request: KibaApiRequest[endpoints.ListBarbellActionsRequest]) -> endpoints.ListBarbellActionsResponse:
        userId = request.authBasic.username  # type: ignore[union-attr]
        barbell = await _get_authorized_barbell(userId=userId, barbellId=request.path_params['barbellId'])
        actions = await systemManager.list_barbell_actions(barbellId=barbell.barbellId)
        return endpoints.ListBarbellActionsResponse(actions=[resourceBuilder.action_from_model(action=action) for action in actions])

    @json_route(requestType=endpoints.ListChatMessagesRequest, responseType=endpoints.ListChatMessagesResponse)
    @authorize_signature(authorizer=systemManager)
    async def list_chat_messages(request: KibaApiRequest[endpoints.ListChatMessagesRequest]) -> endpoints.ListChatMessagesResponse:
        userId = request.authBasic.username  # type: ignore[union-attr]
        barbell = await _get_authorized_barbell(userId=userId, barbellId=request.path_params['barbellId'])
        chatEvents = await systemManager.conversationManager.list_chat_events(userId=userId, barbellId=barbell.barbellId)
        return endpoints.ListChatMessagesResponse(messages=[resourceBuilder.chat_message_from_model(chatEvent=chatEvent) for chatEvent in chatEvents])

    @streaming_json_route(requestType=endpoints.AddUserMessageStreamedRequest, responseType=endpoints.AddUserMessageStreamedResponse)
    @authorize_signature(authorizer=systemManager)
    async def add_user_message_streamed(request: KibaApiRequest[endpoints.AddUserMessageStreamedRequest]) -> typing.AsyncIterator[endpoints.AddUserMessageStreamedResponse]:
        userId = request.authBasic.username  # type: ignore[union-attr]
        barbell = await _get_authorized_barbell(userId=userId, barbellId=request.path_params['barbellId'])
        async for chatEvent in systemManager.conversationManager.add_user_message(userId=userId, barbell=barbell, content=request.data.content):
            yield endpoints.AddUserMessageStreamedResponse(message=resourceBuilder.chat_message_from_model(chatEvent=chatEvent))

    @streaming_json_route(requestType=endpoints.AddCreationMessageStreamedRequest, responseType=endpoints.AddUserMessageStreamedResponse)
    @authorize_signature(authorizer=systemManager)
    async def add_creation_message_streamed(request: KibaApiRequest[endpoints.AddCreationMessageStreamedRequest]) -> typing.AsyncIterator[endpoints.AddUserMessageStreamedResponse]:
        userId = request.authBasic.username  # type: ignore[union-attr]
        draftContext = '\n'.join([
            f'Name: {request.data.name.strip() or "(not set)"}',
            'Safe leg: SGOV (fixed)',
            f'Satellite leg address: {request.data.satelliteAssetAddress}',
            f'Maximum drawdown budget: {request.data.maxDrawdownBps / 100:.2f}%',
            f'Target satellite exposure: {request.data.targetSatelliteBps / 100:.2f}%',
            f'Maximum satellite exposure: {request.data.maxSatelliteBps / 100:.2f}%',
        ])
        async for chatEvent in systemManager.conversationManager.add_creation_message(
            userId=userId,
            conversationId=request.path_params['conversationId'],
            content=request.data.content,
            draftContext=draftContext,
        ):
            yield endpoints.AddUserMessageStreamedResponse(message=resourceBuilder.chat_message_from_model(chatEvent=chatEvent))

    return [
        Route('/logins', login, methods=['POST']),
        Route('/users', create_user, methods=['POST']),
        Route('/chains/{chainId:int}/barbell-assets', list_barbell_assets, methods=['GET']),
        Route('/barbells', get_barbell, methods=['GET']),
        Route('/barbells', create_barbell, methods=['POST']),
        Route('/barbells/{barbellId}/deactivate', deactivate_barbell, methods=['POST']),
        Route('/barbells/{barbellId}/portfolio', get_barbell_portfolio, methods=['GET']),
        Route('/barbells/{barbellId}/risk-state', get_barbell_risk_state, methods=['GET']),
        Route('/barbells/{barbellId}/risk-budget', set_risk_budget, methods=['POST']),
        Route('/barbells/{barbellId}/snapshots', list_barbell_snapshots, methods=['GET']),
        Route('/barbells/{barbellId}/actions', list_barbell_actions, methods=['GET']),
        Route('/barbells/{barbellId}/messages', list_chat_messages, methods=['GET']),
        Route('/barbells/{barbellId}/messages-streamed', add_user_message_streamed, methods=['POST']),
        Route('/barbells/creation-conversations/{conversationId}/messages-streamed', add_creation_message_streamed, methods=['POST']),
    ]
