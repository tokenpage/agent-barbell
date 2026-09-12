"""add barbell name

Revision ID: d7c4b9a1c2e3
Revises: f9e51aa900fd
Create Date: 2026-09-12 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd7c4b9a1c2e3'
down_revision = 'f9e51aa900fd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tbl_barbells', sa.Column('name', sa.Text(), nullable=False, server_default='Agent Barbell'))
    op.alter_column('tbl_barbells', 'name', server_default=None)


def downgrade():
    op.drop_column('tbl_barbells', 'name')
