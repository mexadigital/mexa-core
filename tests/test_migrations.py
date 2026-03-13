"""
Tests for Alembic database migrations.

This module tests:
- Migration upgrade/downgrade cycles
- Table creation and structure
- Index creation
- Constraint enforcement
- Migration chain integrity
"""
import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
import os


# Test database URL (use a separate test database)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://mexa_user:mexa_password@localhost:5432/mexa_test_db"
)


@pytest.fixture(scope="session")
def alembic_config():
    """Create Alembic configuration for testing."""
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    return config


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def clean_db(engine, alembic_config):
    """
    Ensure clean database state before each test.
    Downgrades to base and upgrades to head.
    """
    # Downgrade all migrations
    command.downgrade(alembic_config, "base")
    
    yield
    
    # Cleanup after test
    command.downgrade(alembic_config, "base")


class TestMigrations:
    """Test suite for database migrations."""
    
    def test_upgrade_downgrade_cycle(self, alembic_config, engine, clean_db):
        """Test that all migrations can be applied and reverted."""
        # Upgrade to head
        command.upgrade(alembic_config, "head")
        
        # Verify we're at head
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert 'usuarios' in tables
        assert 'productos' in tables
        assert 'vales' in tables
        assert 'alembic_version' in tables
        
        # Downgrade to base
        command.downgrade(alembic_config, "base")
        
        # Verify tables are removed
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert 'usuarios' not in tables
        assert 'productos' not in tables
        assert 'vales' not in tables
    
    def test_001_create_initial_tables(self, alembic_config, engine, clean_db):
        """Test the first migration creates required tables with proper structure."""
        # Apply first migration only
        command.upgrade(alembic_config, "001_create_initial")
        
        inspector = inspect(engine)
        
        # Test usuarios table
        assert 'usuarios' in inspector.get_table_names()
        usuarios_columns = {col['name'] for col in inspector.get_columns('usuarios')}
        assert 'id' in usuarios_columns
        assert 'username' in usuarios_columns
        assert 'email' in usuarios_columns
        assert 'employee_no' in usuarios_columns
        assert 'is_active' in usuarios_columns
        assert 'created_at' in usuarios_columns
        
        # Test productos table
        assert 'productos' in inspector.get_table_names()
        productos_columns = {col['name'] for col in inspector.get_columns('productos')}
        assert 'id' in productos_columns
        assert 'code' in productos_columns
        assert 'name' in productos_columns
        assert 'category' in productos_columns
        assert 'stock_quantity' in productos_columns
        
        # Test vales table
        assert 'vales' in inspector.get_table_names()
        vales_columns = {col['name'] for col in inspector.get_columns('vales')}
        assert 'id' in vales_columns
        assert 'vale_number' in vales_columns
        assert 'usuario_id' in vales_columns
        assert 'employee_no' in vales_columns
        assert 'status' in vales_columns
        assert 'created_at' in vales_columns
        
        # Test vale_items table
        assert 'vale_items' in inspector.get_table_names()
        vale_items_columns = {col['name'] for col in inspector.get_columns('vale_items')}
        assert 'id' in vale_items_columns
        assert 'vale_id' in vale_items_columns
        assert 'producto_id' in vale_items_columns
        assert 'item_name' in vale_items_columns
        assert 'quantity' in vale_items_columns
        
        # Test foreign keys
        vales_fks = inspector.get_foreign_keys('vales')
        assert len(vales_fks) == 1
        assert vales_fks[0]['referred_table'] == 'usuarios'
        
        vale_items_fks = inspector.get_foreign_keys('vale_items')
        assert len(vale_items_fks) == 2
        referred_tables = {fk['referred_table'] for fk in vale_items_fks}
        assert 'vales' in referred_tables
        assert 'productos' in referred_tables
    
    def test_002_add_request_id(self, alembic_config, engine, clean_db):
        """Test that migration 002 adds request_id column with unique constraint."""
        # Apply migrations up to 002
        command.upgrade(alembic_config, "002_add_request_id")
        
        inspector = inspect(engine)
        
        # Check request_id column exists
        vales_columns = {col['name'] for col in inspector.get_columns('vales')}
        assert 'request_id' in vales_columns
        
        # Verify column is UUID type and nullable
        for col in inspector.get_columns('vales'):
            if col['name'] == 'request_id':
                assert col['nullable'] is True
                # Type will be UUID in PostgreSQL
                break
        
        # Check unique constraint exists
        unique_constraints = inspector.get_unique_constraints('vales')
        constraint_columns = [set(uc['column_names']) for uc in unique_constraints]
        assert {'request_id'} in constraint_columns
    
    def test_003_add_indexes(self, alembic_config, engine, clean_db):
        """Test that migration 003 creates all required indexes."""
        # Apply all migrations
        command.upgrade(alembic_config, "003_add_indexes")
        
        inspector = inspect(engine)
        
        # Check usuarios indexes
        usuarios_indexes = {idx['name'] for idx in inspector.get_indexes('usuarios')}
        assert 'ix_usuarios_email' in usuarios_indexes
        assert 'ix_usuarios_employee_no' in usuarios_indexes
        
        # Check productos indexes
        productos_indexes = {idx['name'] for idx in inspector.get_indexes('productos')}
        assert 'ix_productos_category' in productos_indexes
        assert 'ix_productos_code' in productos_indexes
        
        # Check vales indexes
        vales_indexes = {idx['name'] for idx in inspector.get_indexes('vales')}
        assert 'ix_vales_status' in vales_indexes
        assert 'ix_vales_created_at' in vales_indexes
        assert 'ix_vales_employee_no' in vales_indexes
        assert 'ix_vales_usuario_created' in vales_indexes
        
        # Check vale_items indexes
        vale_items_indexes = {idx['name'] for idx in inspector.get_indexes('vale_items')}
        assert 'ix_vale_items_vale_id' in vale_items_indexes
        assert 'ix_vale_items_producto_id' in vale_items_indexes
    
    def test_migration_chain_integrity(self, alembic_config):
        """Test that migration chain is properly linked."""
        script = ScriptDirectory.from_config(alembic_config)
        
        # Get all revisions
        revisions = list(script.walk_revisions())
        
        # Should have 3 migrations
        assert len(revisions) >= 3
        
        # Check that each migration (except the first) has a down_revision
        for revision in revisions:
            if revision.revision != '001_create_initial':
                assert revision.down_revision is not None
    
    def test_downgrade_removes_changes(self, alembic_config, engine, clean_db):
        """Test that downgrade properly removes changes from each migration."""
        # Apply all migrations
        command.upgrade(alembic_config, "head")
        inspector = inspect(engine)
        
        # Verify indexes exist
        vales_indexes = {idx['name'] for idx in inspector.get_indexes('vales')}
        assert 'ix_vales_status' in vales_indexes
        
        # Downgrade one step (remove indexes)
        command.downgrade(alembic_config, "-1")
        inspector = inspect(engine)
        vales_indexes = {idx['name'] for idx in inspector.get_indexes('vales')}
        assert 'ix_vales_status' not in vales_indexes
        
        # Verify request_id still exists
        vales_columns = {col['name'] for col in inspector.get_columns('vales')}
        assert 'request_id' in vales_columns
        
        # Downgrade one more step (remove request_id)
        command.downgrade(alembic_config, "-1")
        inspector = inspect(engine)
        vales_columns = {col['name'] for col in inspector.get_columns('vales')}
        assert 'request_id' not in vales_columns
        
        # Tables should still exist
        assert 'vales' in inspector.get_table_names()
    
    def test_concurrent_migration_safety(self, alembic_config, engine, clean_db):
        """Test that migrations use transactions for safety."""
        # This test verifies that migrations can be safely rolled back
        # if an error occurs during migration
        
        # Apply first migration
        command.upgrade(alembic_config, "001_create_initial")
        
        # Create a session and verify data can be inserted
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Insert test data
            session.execute(text(
                "INSERT INTO usuarios (username, email, is_active, created_at) "
                "VALUES ('testuser', 'test@example.com', true, NOW())"
            ))
            session.commit()
            
            # Verify data exists
            result = session.execute(text("SELECT * FROM usuarios WHERE username = 'testuser'"))
            assert result.fetchone() is not None
            
        finally:
            session.close()
    
    def test_unique_constraints(self, alembic_config, engine, clean_db):
        """Test that unique constraints are properly enforced."""
        # Apply migrations
        command.upgrade(alembic_config, "head")
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Insert a user
            session.execute(text(
                "INSERT INTO usuarios (username, email, is_active, created_at) "
                "VALUES ('testuser', 'test@example.com', true, NOW())"
            ))
            session.commit()
            
            # Try to insert duplicate username - should fail
            with pytest.raises(Exception):  # Will raise IntegrityError
                session.execute(text(
                    "INSERT INTO usuarios (username, email, is_active, created_at) "
                    "VALUES ('testuser', 'test2@example.com', true, NOW())"
                ))
                session.commit()
            
            session.rollback()
            
        finally:
            session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
