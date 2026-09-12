import sqlalchemy
from sqlalchemy.dialects import postgresql as sqlalchemy_psql

from agent_barbell.model import User
from agent_barbell.store.entity_repository import EntityRepository

metadata = sqlalchemy.MetaData()

UsersTable = sqlalchemy.Table(
    'tbl_users',
    metadata,
    sqlalchemy.Column(key='userId', name='id', type_=sqlalchemy_psql.UUID, primary_key=True),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='walletAddress', name='wallet_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='username', name='username', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.UniqueConstraint('walletAddress', name='tbl_users_ux_wallet_address'),
)

UsersRepository = EntityRepository(table=UsersTable, modelClass=User)
