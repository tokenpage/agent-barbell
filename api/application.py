import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from core import logging
from core.api.default_routes import create_default_routes
from core.api.middleware.database_connection_middleware import DatabaseConnectionMiddleware
from core.api.middleware.exception_handling_middleware import ExceptionHandlingMiddleware
from core.api.middleware.logging_middleware import LoggingMiddleware
from core.api.middleware.server_headers_middleware import ServerHeadersMiddleware
from core.util.value_holder import RequestIdHolder
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.routing import Mount

from agent_barbell.api.v1_api import create_v1_routes
from agent_barbell.create_system_manager import create_system_manager
from agent_barbell.create_system_manager import use_system_manager

name = os.environ.get('NAME', 'agent-barbell-api')
version = os.environ.get('VERSION', 'local')
environment = os.environ.get('ENV', 'dev')
isRunningDebugMode = environment == 'dev'

requestIdHolder = RequestIdHolder()
if isRunningDebugMode:
    logging.init_basic_logging()
else:
    logging.init_json_logging(name=name, version=version, environment=environment, requestIdHolder=requestIdHolder)

systemManager = create_system_manager()


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:  # noqa: ARG001
    async with use_system_manager(systemManager=systemManager, databasePoolSize=2 if isRunningDebugMode else 25):
        yield


app = Starlette(
    routes=[
        *create_default_routes(name=name, version=version, environment=environment),
        Mount(
            path='/v1',
            routes=[
                *create_v1_routes(systemManager=systemManager),
            ],
        ),
    ],
    lifespan=lifespan,
)
app.add_middleware(ExceptionHandlingMiddleware, shouldSquashClientExceptions=environment != 'dev', shouldHideInternalErrors=environment != 'dev')
app.add_middleware(ServerHeadersMiddleware, name=name, version=version, environment=environment)
app.add_middleware(LoggingMiddleware, requestIdHolder=requestIdHolder)
app.add_middleware(DatabaseConnectionMiddleware, database=systemManager.userManager.database)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=9)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['*'],
    allow_origins=[
        'http://localhost:3000',
        'http://localhost:3100',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:3100',
        os.environ.get('KRT_APP_URL', 'https://agent-barbell.yieldseeker.xyz'),
    ],
    allow_origin_regex=r'https://([a-z0-9-]+\.)*agent-barbell\.yieldseeker\.xyz',
)
