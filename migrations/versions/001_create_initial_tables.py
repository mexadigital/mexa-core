"""Create initial tables for usuarios, productos, and vales

Revision ID: 001_create_initial
Revises: 
Create Date: 2024-01-01 10:00:00.000000

This migration creates the core tables for the mexa-core application:
- usuarios: User management table
- productos: Product catalog table  
- vales: Vouchers/tickets table for tracking equipment and consumables

These tables form the foundation of the application's data model.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_create_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Apply the migration changes.
    
    Creates the initial database schema with usuarios, productos, and vales tables.
    All tables include primary keys and timestamps for audit purposes.
    """
    # Create usuarios (users) table
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('employee_no', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # Create productos (products) table
    op.create_table(
        'productos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('stock_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('min_stock', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create vales (vouchers) table
    op.create_table(
        'vales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vale_number', sa.String(length=50), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('employee_no', sa.String(length=50), nullable=False),
        sa.Column('employee_name', sa.String(length=255), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('signed_physical', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('safety_engineer', sa.String(length=255), nullable=True),
        sa.Column('photo_path', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVO'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('vale_number')
    )
    
    # Create vale_items table (items in each vale)
    op.create_table(
        'vale_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vale_id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=True),
        sa.Column('kind', sa.String(length=50), nullable=False),
        sa.Column('item_name', sa.String(length=255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('origin_location', sa.String(length=100), nullable=False),
        sa.Column('motive', sa.String(length=100), nullable=False),
        sa.Column('tool_state', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['vale_id'], ['vales.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['producto_id'], ['productos.id'], ondelete='SET NULL')
    )


def downgrade() -> None:
    """
    Revert the migration changes.
    
    Drops all tables created in upgrade(), in reverse order to respect
    foreign key constraints.
    """
    op.drop_table('vale_items')
    op.drop_table('vales')
    op.drop_table('productos')
    op.drop_table('usuarios')
