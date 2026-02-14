"""Add request_id to vales table

Revision ID: 002_add_request_id
Revises: 001_create_initial
Create Date: 2024-01-15 14:30:00.000000

This migration adds a request_id UUID column to the vales table for tracking
external request identifiers. This was introduced in version 1.2 to enable
better integration with external systems and provide unique request tracking.

The request_id is:
- A UUID type for global uniqueness
- UNIQUE to prevent duplicate requests
- Nullable to support existing records
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '002_add_request_id'
down_revision: Union[str, None] = '001_create_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Apply the migration changes.
    
    Adds request_id UUID UNIQUE column to vales table for tracking external requests.
    The column is nullable to support existing records.
    """
    # Add request_id column as UUID with UNIQUE constraint
    op.add_column(
        'vales',
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    
    # Create unique constraint on request_id
    # This ensures no duplicate request IDs can be inserted
    op.create_unique_constraint(
        'uq_vales_request_id',
        'vales',
        ['request_id']
    )


def downgrade() -> None:
    """
    Revert the migration changes.
    
    Removes the request_id column and its unique constraint from vales table.
    """
    # Drop the unique constraint first
    op.drop_constraint('uq_vales_request_id', 'vales', type_='unique')
    
    # Drop the column
    op.drop_column('vales', 'request_id')
