"""Add match_id to winner_prizes

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-06-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'c3d4e5f6a7b8'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'winner_prizes' not in tables:
        # Tabla no existe (instancia limpia que solo corrió migraciones sin db.create_all)
        op.create_table('winner_prizes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('match_id', sa.Integer(), nullable=True),
            sa.Column('bono_code', sa.String(length=50), nullable=False),
            sa.Column('prize_name', sa.String(length=150), nullable=False),
            sa.Column('image_url', sa.String(length=500), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('email_sent', sa.Boolean(), nullable=True),
            sa.Column('claimed_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['match_id'], ['matches.id']),
            sa.ForeignKeyConstraint(['user_id'], ['user.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('bono_code'),
        )
    else:
        # Tabla ya existe — solo agregar match_id si no está
        columns = [col['name'] for col in inspector.get_columns('winner_prizes')]
        if 'match_id' not in columns:
            with op.batch_alter_table('winner_prizes', schema=None) as batch_op:
                batch_op.add_column(sa.Column('match_id', sa.Integer(), nullable=True))
                batch_op.create_foreign_key(
                    'fk_winner_prizes_match_id', 'matches', ['match_id'], ['id']
                )


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'winner_prizes' in tables:
        columns = [col['name'] for col in inspector.get_columns('winner_prizes')]
        if 'match_id' in columns:
            with op.batch_alter_table('winner_prizes', schema=None) as batch_op:
                batch_op.drop_column('match_id')
