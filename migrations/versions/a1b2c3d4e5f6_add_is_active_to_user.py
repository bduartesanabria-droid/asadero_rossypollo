"""Add is_active column to user

Revision ID: a1b2c3d4e5f6
Revises: 3f3c20ba7d6c
Create Date: 2026-06-09 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '3f3c20ba7d6c'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_active')
