"""Add indexes to usuarios table

Revision ID: 003
Revises: 002
Create Date: 2024-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Add additional indexes to usuarios table"""
    # Add created_at index for query optimization
    op.create_index('ix_usuarios_created_at', 'usuarios', ['created_at'])


def downgrade():
    """Remove additional indexes from usuarios table"""
    op.drop_index('ix_usuarios_created_at', table_name='usuarios')
