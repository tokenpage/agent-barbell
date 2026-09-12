import sqlalchemy
from sqlalchemy.dialects import postgresql as sqlalchemy_psql

from agent_barbell.model import Barbell
from agent_barbell.model import BarbellAction
from agent_barbell.model import BarbellPolicy
from agent_barbell.model import ChatEvent
from agent_barbell.model import PriceTick
from agent_barbell.model import RiskSnapshot
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

BarbellsTable = sqlalchemy.Table(
    'tbl_barbells',
    metadata,
    sqlalchemy.Column(key='barbellId', name='id', type_=sqlalchemy_psql.UUID, primary_key=True),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='userId', name='user_id', type_=sqlalchemy_psql.UUID, nullable=False),
    sqlalchemy.Column(key='name', name='name', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='chainId', name='chain_id', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='walletAddress', name='wallet_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='ownerAddress', name='owner_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='anchorAssetAddress', name='anchor_asset_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='satelliteAssetAddress', name='satellite_asset_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='isActive', name='is_active', type_=sqlalchemy.Boolean, nullable=False),
    sqlalchemy.UniqueConstraint('walletAddress', name='tbl_barbells_ux_wallet_address'),
    sqlalchemy.Index('tbl_barbells_idx_user_id', 'userId'),
)

BarbellsRepository = EntityRepository(table=BarbellsTable, modelClass=Barbell)

BarbellPoliciesTable = sqlalchemy.Table(
    'tbl_barbell_policies',
    metadata,
    sqlalchemy.Column(key='barbellPolicyId', name='id', type_=sqlalchemy_psql.UUID, primary_key=True),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='barbellId', name='barbell_id', type_=sqlalchemy_psql.UUID, nullable=False),
    sqlalchemy.Column(key='maxDrawdownBps', name='max_drawdown_bps', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='targetSatelliteBps', name='target_satellite_bps', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='maxSatelliteBps', name='max_satellite_bps', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='isKilled', name='is_killed', type_=sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(key='transactionHash', name='transaction_hash', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Index('tbl_barbell_policies_idx_barbell_id', 'barbellId'),
)

BarbellPoliciesRepository = EntityRepository(table=BarbellPoliciesTable, modelClass=BarbellPolicy)

PriceTicksTable = sqlalchemy.Table(
    'tbl_price_ticks',
    metadata,
    sqlalchemy.Column(key='priceTickId', name='id', type_=sqlalchemy_psql.UUID, primary_key=True),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='chainId', name='chain_id', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='assetAddress', name='asset_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='blockNumber', name='block_number', type_=sqlalchemy.BigInteger, nullable=False),
    sqlalchemy.Column(key='blockDate', name='block_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='priceUsd', name='price_usd', type_=sqlalchemy.Float, nullable=False),
    sqlalchemy.UniqueConstraint('chainId', 'assetAddress', 'blockNumber', name='tbl_price_ticks_ux_chain_asset_block'),
    sqlalchemy.Index('tbl_price_ticks_idx_asset_date', 'assetAddress', 'blockDate'),
)

PriceTicksRepository = EntityRepository(table=PriceTicksTable, modelClass=PriceTick)

RiskSnapshotsTable = sqlalchemy.Table(
    'tbl_risk_snapshots',
    metadata,
    sqlalchemy.Column(key='riskSnapshotId', name='id', type_=sqlalchemy_psql.UUID, primary_key=True),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='barbellId', name='barbell_id', type_=sqlalchemy_psql.UUID, nullable=False),
    sqlalchemy.Column(key='snapshotDate', name='snapshot_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='totalValueUsd', name='total_value_usd', type_=sqlalchemy.Float, nullable=False),
    sqlalchemy.Column(key='anchorValueUsd', name='anchor_value_usd', type_=sqlalchemy.Float, nullable=False),
    sqlalchemy.Column(key='satelliteValueUsd', name='satellite_value_usd', type_=sqlalchemy.Float, nullable=False),
    sqlalchemy.Column(key='cashValueUsd', name='cash_value_usd', type_=sqlalchemy.Float, nullable=False),
    sqlalchemy.Column(key='satelliteBps', name='satellite_bps', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='peakValueUsd', name='peak_value_usd', type_=sqlalchemy.Float, nullable=False),
    sqlalchemy.Column(key='drawdownBps', name='drawdown_bps', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='volatility', name='volatility', type_=sqlalchemy.Float, nullable=False),
    sqlalchemy.Column(key='momentum', name='momentum', type_=sqlalchemy.Float, nullable=False),
    sqlalchemy.Column(key='targetSatelliteBps', name='target_satellite_bps', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Index('tbl_risk_snapshots_idx_barbell_date', 'barbellId', 'snapshotDate'),
)

RiskSnapshotsRepository = EntityRepository(table=RiskSnapshotsTable, modelClass=RiskSnapshot)

BarbellActionsTable = sqlalchemy.Table(
    'tbl_barbell_actions',
    metadata,
    sqlalchemy.Column(key='barbellActionId', name='id', type_=sqlalchemy_psql.UUID, primary_key=True),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='barbellId', name='barbell_id', type_=sqlalchemy_psql.UUID, nullable=False),
    sqlalchemy.Column(key='actionType', name='action_type', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='fromSatelliteBps', name='from_satellite_bps', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='toSatelliteBps', name='to_satellite_bps', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='reason', name='reason', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='decisionTrace', name='decision_trace', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='transactionHash', name='transaction_hash', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Index('tbl_barbell_actions_idx_barbell_id', 'barbellId'),
)

BarbellActionsRepository = EntityRepository(table=BarbellActionsTable, modelClass=BarbellAction)

ChatEventsTable = sqlalchemy.Table(
    'tbl_chat_events',
    metadata,
    sqlalchemy.Column(key='chatEventId', name='id', type_=sqlalchemy_psql.UUID, primary_key=True),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='userId', name='user_id', type_=sqlalchemy_psql.UUID, nullable=False),
    sqlalchemy.Column(key='barbellId', name='barbell_id', type_=sqlalchemy_psql.UUID, nullable=False),
    sqlalchemy.Column(key='conversationId', name='conversation_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='eventType', name='event_type', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='content', name='content', type_=sqlalchemy_psql.JSONB, nullable=False),
    sqlalchemy.Index('tbl_chat_events_idx_conversation', 'barbellId', 'conversationId', 'createdDate'),
)

ChatEventsRepository = EntityRepository(table=ChatEventsTable, modelClass=ChatEvent)
