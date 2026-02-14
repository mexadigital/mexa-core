"""
Test configuration and fixtures for multi-tenant tests
"""
import pytest
from app.app_factory import create_app, db
from app.auth_utils import hash_password


@pytest.fixture(scope='function')
def app():
    """Create and configure a test app instance"""
    app = create_app('testing')
    
    with app.app_context():
        from app.models_multitenant import init_models
        Tenant, Usuario, Producto, Vale, AuditLog = init_models(db)
        app.models = {
            'Tenant': Tenant,
            'Usuario': Usuario,
            'Producto': Producto,
            'Vale': Vale,
            'AuditLog': AuditLog
        }
        
        db.create_all()
        
        # Get models
        Tenant = app.models['Tenant']
        
        # Create test tenants
        tenant1 = Tenant(
            id=1,
            slug='tenant1',
            nombre='Tenant One',
            email='admin@tenant1.com',
            plan='pro',
            activo=True
        )
        tenant2 = Tenant(
            id=2,
            slug='tenant2',
            nombre='Tenant Two',
            email='admin@tenant2.com',
            plan='basic',
            activo=True
        )
        db.session.add(tenant1)
        db.session.add(tenant2)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def tenant1_user(app):
    """Create a user in tenant1"""
    with app.app_context():
        Usuario = app.models['Usuario']
        
        user = Usuario(
            tenant_id=1,
            email='user1@tenant1.com',
            nombre='User One',
            password_hash=hash_password('password123'),
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        
        # Return user data
        return {
            'id': user.id,
            'tenant_id': user.tenant_id,
            'email': user.email,
            'password': 'password123'
        }


@pytest.fixture(scope='function')
def tenant2_user(app):
    """Create a user in tenant2"""
    with app.app_context():
        Usuario = app.models['Usuario']
        
        user = Usuario(
            tenant_id=2,
            email='user2@tenant2.com',
            nombre='User Two',
            password_hash=hash_password('password456'),
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'tenant_id': user.tenant_id,
            'email': user.email,
            'password': 'password456'
        }


@pytest.fixture(scope='function')
def tenant1_token(client, tenant1_user):
    """Get JWT token for tenant1 user"""
    response = client.post('/api/auth/login', json={
        'email': tenant1_user['email'],
        'password': tenant1_user['password'],
        'tenant_slug': 'tenant1'
    })
    data = response.get_json()
    return data['access_token']


@pytest.fixture(scope='function')
def tenant2_token(client, tenant2_user):
    """Get JWT token for tenant2 user"""
    response = client.post('/api/auth/login', json={
        'email': tenant2_user['email'],
        'password': tenant2_user['password'],
        'tenant_slug': 'tenant2'
    })
    data = response.get_json()
    return data['access_token']


@pytest.fixture(scope='function')
def tenant1_producto(app, tenant1_user):
    """Create a product in tenant1"""
    with app.app_context():
        Producto = app.models['Producto']
        
        producto = Producto(
            tenant_id=1,
            nombre='Product Tenant1',
            descripcion='Test product',
            sku='SKU-T1-001',
            precio=100.00,
            stock=50,
            activo=True
        )
        db.session.add(producto)
        db.session.commit()
        
        return {
            'id': producto.id,
            'tenant_id': producto.tenant_id,
            'nombre': producto.nombre,
            'stock': producto.stock
        }


@pytest.fixture(scope='function')
def tenant2_producto(app, tenant2_user):
    """Create a product in tenant2"""
    with app.app_context():
        Producto = app.models['Producto']
        
        producto = Producto(
            tenant_id=2,
            nombre='Product Tenant2',
            descripcion='Test product',
            sku='SKU-T2-001',
            precio=200.00,
            stock=30,
            activo=True
        )
        db.session.add(producto)
        db.session.commit()
        
        return {
            'id': producto.id,
            'tenant_id': producto.tenant_id,
            'nombre': producto.nombre,
            'stock': producto.stock
        }
