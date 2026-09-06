"""
Alembic migration: Add multi-tenant support

Revision ID: 005
Create Date: 2026-02-14

This migration adds multi-tenant support with strict safety constraints:
- Creates tenants table with default tenant
- Adds tenant_id to all main tables
- Uses server_default instead of default= in column definitions
- Creates default tenant BEFORE updating existing records
- NO ondelete='CASCADE' to prevent accidental data loss
- All new columns: NOT NULL only after data is backfilled
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '005'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    Upgrade database schema to support multi-tenancy
    """
    # ==========================================================================
    # STEP 1: Create tenants table
    # ==========================================================================
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(50), unique=True, nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('plan', sa.String(50), nullable=False, server_default='basic'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_tenants_slug', 'tenants', ['slug'])
    
    # ==========================================================================
    # STEP 2: Insert default tenant BEFORE adding NOT NULL constraint
    # ==========================================================================
    op.execute("""
        INSERT INTO tenants (id, slug, nombre, email, plan, activo, created_at, updated_at)
        VALUES (1, 'default', 'Default Tenant', 'admin@mexa.local', 'pro', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """)
    
    # ==========================================================================
    # STEP 3: Add tenant_id to usuarios table
    # ==========================================================================
    # Add column as nullable initially
    op.add_column('usuarios', sa.Column('tenant_id', sa.Integer(), nullable=True))
    
    # Backfill with default tenant
    op.execute("UPDATE usuarios SET tenant_id = 1 WHERE tenant_id IS NULL")
    
    # Make NOT NULL and add constraint (NO CASCADE)
    op.alter_column('usuarios', 'tenant_id', nullable=False)
    op.create_foreign_key(
        'fk_usuarios_tenant_id',
        'usuarios', 'tenants',
        ['tenant_id'], ['id']
        # NOTE: NO ondelete='CASCADE' - manual cleanup only
    )
    op.create_index('ix_usuarios_tenant_id', 'usuarios', ['tenant_id'])
    
    # Create unique constraint for (tenant_id, email)
    # First drop old unique constraint on email if it exists
    try:
        op.drop_constraint('uq_usuarios_email', 'usuarios', type_='unique')
    except:
        pass  # Constraint may not exist
    op.create_unique_constraint('uq_usuarios_tenant_email', 'usuarios', ['tenant_id', 'email'])
    
    # ==========================================================================
    # STEP 4: Add tenant_id to productos table
    # ==========================================================================
    # Add column as nullable initially
    op.add_column('productos', sa.Column('tenant_id', sa.Integer(), nullable=True))
    
    # Backfill with default tenant
    op.execute("UPDATE productos SET tenant_id = 1 WHERE tenant_id IS NULL")
    
    # Make NOT NULL and add constraint (NO CASCADE)
    op.alter_column('productos', 'tenant_id', nullable=False)
    op.create_foreign_key(
        'fk_productos_tenant_id',
        'productos', 'tenants',
        ['tenant_id'], ['id']
        # NOTE: NO ondelete='CASCADE'
    )
    op.create_index('ix_productos_tenant_id', 'productos', ['tenant_id'])
    op.create_index('ix_productos_tenant_sku', 'productos', ['tenant_id', 'sku'])
    
    # Create unique constraint for (tenant_id, nombre)
    # First drop old unique constraint on nombre if it exists
    try:
        op.drop_constraint('uq_productos_nombre', 'productos', type_='unique')
    except:
        pass  # Constraint may not exist
    op.create_unique_constraint('uq_productos_tenant_nombre', 'productos', ['tenant_id', 'nombre'])
    
    # ==========================================================================
    # STEP 5: Add tenant_id to vales table
    # ==========================================================================
    # Add column as nullable initially
    op.add_column('vales', sa.Column('tenant_id', sa.Integer(), nullable=True))
    
    # Backfill with default tenant
    op.execute("UPDATE vales SET tenant_id = 1 WHERE tenant_id IS NULL")
    
    # Make NOT NULL and add constraint (NO CASCADE)
    op.alter_column('vales', 'tenant_id', nullable=False)
    op.create_foreign_key(
        'fk_vales_tenant_id',
        'vales', 'tenants',
        ['tenant_id'], ['id']
        # NOTE: NO ondelete='CASCADE'
    )
    op.create_index('ix_vales_tenant_id', 'vales', ['tenant_id'])
    op.create_index('ix_vales_tenant_estado', 'vales', ['tenant_id', 'estado'])
    
    # Ensure request_id is indexed and unique
    op.create_index('ix_vales_request_id', 'vales', ['request_id'], unique=True)
    
    # ==========================================================================
    # STEP 6: Add tenant_id to audit_logs table
    # ==========================================================================
    # Add column as nullable initially
    op.add_column('audit_logs', sa.Column('tenant_id', sa.Integer(), nullable=True))
    
    # Backfill with default tenant
    op.execute("UPDATE audit_logs SET tenant_id = 1 WHERE tenant_id IS NULL")
    
    # Make NOT NULL and add constraint (NO CASCADE)
    op.alter_column('audit_logs', 'tenant_id', nullable=False)
    op.create_foreign_key(
        'fk_audit_logs_tenant_id',
        'audit_logs', 'tenants',
        ['tenant_id'], ['id']
        # NOTE: NO ondelete='CASCADE'
    )
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'])
    op.create_index('ix_audit_logs_tenant_entidad', 'audit_logs', ['tenant_id', 'entidad_tipo', 'entidad_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade():
    """
    Downgrade database schema (remove multi-tenant support)
    
    WARNING: This will remove tenant isolation. Use with caution.
    """
    # Drop audit_logs indexes and constraints
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_tenant_entidad', table_name='audit_logs')
    op.drop_index('ix_audit_logs_tenant_id', table_name='audit_logs')
    op.drop_constraint('fk_audit_logs_tenant_id', 'audit_logs', type_='foreignkey')
    op.drop_column('audit_logs', 'tenant_id')
    
    # Drop vales indexes and constraints
    op.drop_index('ix_vales_request_id', table_name='vales')
    op.drop_index('ix_vales_tenant_estado', table_name='vales')
    op.drop_index('ix_vales_tenant_id', table_name='vales')
    op.drop_constraint('fk_vales_tenant_id', 'vales', type_='foreignkey')
    op.drop_column('vales', 'tenant_id')
    
    # Drop productos indexes and constraints
    op.drop_constraint('uq_productos_tenant_nombre', 'productos', type_='unique')
    op.drop_index('ix_productos_tenant_sku', table_name='productos')
    op.drop_index('ix_productos_tenant_id', table_name='productos')
    op.drop_constraint('fk_productos_tenant_id', 'productos', type_='foreignkey')
    op.drop_column('productos', 'tenant_id')
    
    # Drop usuarios indexes and constraints
    op.drop_constraint('uq_usuarios_tenant_email', 'usuarios', type_='unique')
    op.drop_index('ix_usuarios_tenant_id', table_name='usuarios')
    op.drop_constraint('fk_usuarios_tenant_id', 'usuarios', type_='foreignkey')
    op.drop_column('usuarios', 'tenant_id')
    
    # Drop tenants table
    op.drop_index('ix_tenants_slug', table_name='tenants')
    op.drop_table('tenants')
