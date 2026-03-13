"""Add performance indexes

Revision ID: 003_add_indexes
Revises: 002_add_request_id
Create Date: 2024-02-01 09:00:00.000000

This migration adds strategic indexes to improve query performance:
- Index on usuarios.email for faster user lookups
- Index on productos.category for filtering by category
- Index on vales.status for filtering active/closed vales
- Index on vales.created_at for chronological queries
- Index on vale_items.vale_id for join optimization
- Composite index on vales (usuario_id, created_at) for user history queries

These indexes were identified through production query analysis and will
significantly improve performance for common query patterns.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_indexes'
down_revision: Union[str, None] = '002_add_request_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Apply the migration changes.
    
    Creates performance indexes on frequently queried columns.
    Uses concurrent index creation where possible to minimize locking.
    """
    # Index on usuarios table
    op.create_index(
        'ix_usuarios_email',
        'usuarios',
        ['email'],
        unique=False
    )
    
    op.create_index(
        'ix_usuarios_employee_no',
        'usuarios',
        ['employee_no'],
        unique=False
    )
    
    # Indexes on productos table
    op.create_index(
        'ix_productos_category',
        'productos',
        ['category'],
        unique=False
    )
    
    op.create_index(
        'ix_productos_code',
        'productos',
        ['code'],
        unique=False
    )
    
    # Indexes on vales table
    op.create_index(
        'ix_vales_status',
        'vales',
        ['status'],
        unique=False
    )
    
    op.create_index(
        'ix_vales_created_at',
        'vales',
        ['created_at'],
        unique=False
    )
    
    op.create_index(
        'ix_vales_employee_no',
        'vales',
        ['employee_no'],
        unique=False
    )
    
    # Composite index for user history queries (most recent vales by user)
    op.create_index(
        'ix_vales_usuario_created',
        'vales',
        ['usuario_id', 'created_at'],
        unique=False
    )
    
    # Index on vale_items for join optimization
    op.create_index(
        'ix_vale_items_vale_id',
        'vale_items',
        ['vale_id'],
        unique=False
    )
    
    op.create_index(
        'ix_vale_items_producto_id',
        'vale_items',
        ['producto_id'],
        unique=False
    )


def downgrade() -> None:
    """
    Revert the migration changes.
    
    Drops all performance indexes created in upgrade().
    """
    # Drop vale_items indexes
    op.drop_index('ix_vale_items_producto_id', table_name='vale_items')
    op.drop_index('ix_vale_items_vale_id', table_name='vale_items')
    
    # Drop vales indexes
    op.drop_index('ix_vales_usuario_created', table_name='vales')
    op.drop_index('ix_vales_employee_no', table_name='vales')
    op.drop_index('ix_vales_created_at', table_name='vales')
    op.drop_index('ix_vales_status', table_name='vales')
    
    # Drop productos indexes
    op.drop_index('ix_productos_code', table_name='productos')
    op.drop_index('ix_productos_category', table_name='productos')
    
    # Drop usuarios indexes
    op.drop_index('ix_usuarios_employee_no', table_name='usuarios')
    op.drop_index('ix_usuarios_email', table_name='usuarios')
