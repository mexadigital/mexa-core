"""Add request_id to vales

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Agrega request_id a vales (con UNIQUE)"""
    
    # Enable pgcrypto extension for UUID generation
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    
    # Agregar columna (nullable al principio)
    op.add_column(
        'vales',
        sa.Column('request_id', sa.UUID(as_uuid=True), nullable=True)
    )
    
    # Llenar valores existentes con UUIDs
    op.execute("UPDATE vales SET request_id = gen_random_uuid() WHERE request_id IS NULL")
    
    # Hacer NOT NULL
    op.alter_column('vales', 'request_id', nullable=False)
    
    # Crear UNIQUE CONSTRAINT (solo en vales)
    op.create_unique_constraint(
        'uq_vales_request_id',
        'vales',
        ['request_id']
    )


def downgrade():
    """Remove request_id from vales"""
    op.drop_constraint('uq_vales_request_id', 'vales', type_='unique')
    op.drop_column('vales', 'request_id')
