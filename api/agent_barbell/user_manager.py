from core.store.database import Database
from core.store.retriever import StringFieldFilter
from core.util import chain_util

from agent_barbell.model import User
from agent_barbell.store import schema
from agent_barbell.store.entity_repository import UUIDFieldFilter


class UserManager:
    def __init__(
        self,
        database: Database,
    ) -> None:
        self.database = database

    async def get_user(self, userId: str) -> User:
        return await schema.UsersRepository.get_one(
            database=self.database,
            fieldFilters=[UUIDFieldFilter(fieldName=schema.UsersTable.c.userId.key, eq=userId)],
        )

    async def get_user_by_wallet_address(self, walletAddress: str) -> User:
        return await schema.UsersRepository.get_one(
            database=self.database,
            fieldFilters=[StringFieldFilter(fieldName=schema.UsersTable.c.walletAddress.key, eq=chain_util.normalize_address(value=walletAddress))],
        )

    async def get_user_by_wallet_address_or_none(self, walletAddress: str) -> User | None:
        return await schema.UsersRepository.get_one_or_none(
            database=self.database,
            fieldFilters=[StringFieldFilter(fieldName=schema.UsersTable.c.walletAddress.key, eq=chain_util.normalize_address(value=walletAddress))],
        )

    async def create_user(self, walletAddress: str, username: str | None) -> User:
        return await schema.UsersRepository.create(
            database=self.database,
            walletAddress=chain_util.normalize_address(value=walletAddress),
            username=username,
        )
