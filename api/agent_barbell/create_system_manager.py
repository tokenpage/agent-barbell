import contextlib
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from core import logging
from core.requester import Requester
from core.store.database import Database

from agent_barbell import constants
from agent_barbell.eth_client_manager import EthClientManager
from agent_barbell.eth_client_manager import ThrottledRestEthClient
from agent_barbell.system_manager import SystemManager
from agent_barbell.user_manager import UserManager

DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']
KRT_APP_URL = os.environ['KRT_APP_URL']
AUTH_EXTRA_ALLOWED_DOMAINS = os.environ.get('AUTH_EXTRA_ALLOWED_DOMAINS', '')

PROVIDER_URLS = {
    constants.ROBINHOOD_CHAIN_ID: os.environ[f'RPC_NODE_URL_{constants.ROBINHOOD_CHAIN_ID}'],
}
ARCHIVE_PROVIDER_URLS = {
    constants.ROBINHOOD_CHAIN_ID: os.environ[f'RPC_ARCHIVE_NODE_URL_{constants.ROBINHOOD_CHAIN_ID}'],
}


def create_system_manager() -> SystemManager:
    database = Database(
        connectionString=Database.create_psql_connection_string(
            host=DB_HOST,
            port=DB_PORT,
            name=DB_NAME,
            username=DB_USERNAME,
            password=DB_PASSWORD,
        )
    )
    requester = Requester()
    ethClientManager = EthClientManager()
    for providerChainId, providerUrl in PROVIDER_URLS.items():
        providerClient = ThrottledRestEthClient(url=providerUrl, chainId=providerChainId, requester=requester)
        ethClientManager.register_client(client=providerClient)
    for providerChainId, archiveProviderUrl in ARCHIVE_PROVIDER_URLS.items():
        archiveClient = ThrottledRestEthClient(url=archiveProviderUrl, chainId=providerChainId, requester=requester)
        ethClientManager.register_archive_client(client=archiveClient)
    userManager = UserManager(
        database=database,
    )
    systemManager = SystemManager(
        requester=requester,
        ethClientManager=ethClientManager,
        userManager=userManager,
        appUrl=KRT_APP_URL,
        authExtraAllowedDomains={domain.strip() for domain in AUTH_EXTRA_ALLOWED_DOMAINS.split(',') if domain.strip()},
    )
    return systemManager


async def setup_system_manager(systemManager: SystemManager, databasePoolSize: int = 1) -> None:
    logging.init_external_loggers(loggerNames=['azure', 'httpx', 'httpcore', 'aiosqlite', 'sqlalchemy'])
    await systemManager.userManager.database.connect(poolSize=databasePoolSize)


async def teardown_system_manager(systemManager: SystemManager) -> None:
    with contextlib.suppress(Exception):
        await systemManager.requester.close_connections()
    with contextlib.suppress(Exception):
        await systemManager.userManager.database.disconnect()


@asynccontextmanager
async def use_system_manager(systemManager: SystemManager, databasePoolSize: int = 1) -> AsyncIterator[SystemManager]:
    await setup_system_manager(systemManager=systemManager, databasePoolSize=databasePoolSize)
    try:
        yield systemManager
    finally:
        await teardown_system_manager(systemManager=systemManager)
