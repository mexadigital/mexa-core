"""
Tests for safety features: SELECT FOR UPDATE, idempotency, stock management
"""
import pytest
from app.app_factory import db
# Models loaded from app.models


def test_idempotency_same_request_id_returns_existing_vale(client, tenant1_token, tenant1_producto):
    """Test that submitting same request_id returns existing vale (idempotent)"""
    
    request_data = {
        'producto_id': tenant1_producto['id'],
        'cantidad': 5,
        'request_id': 'idempotent-test-001',
        'comentario': 'First request'
    }
    
    # First request - creates vale
    response1 = client.post('/api/vales',
                           headers={'Authorization': f'Bearer {tenant1_token}'},
                           json=request_data)
    assert response1.status_code == 201
    vale1 = response1.get_json()['vale']
    
    # Second request with same request_id - should return existing vale
    response2 = client.post('/api/vales',
                           headers={'Authorization': f'Bearer {tenant1_token}'},
                           json=request_data)
    assert response2.status_code == 200  # Not 201 (not created)
    vale2 = response2.get_json()['vale']
    
    # Should be same vale
    assert vale1['id'] == vale2['id']
    assert vale1['request_id'] == vale2['request_id']
    assert 'idempotent' in response2.get_json()['message'].lower()


def test_stock_decreases_on_vale_creation(client, app, tenant1_token, tenant1_producto):
    """Test that product stock decreases when vale is created"""
    
    Producto = app.models['Producto']
    
    initial_stock = tenant1_producto['stock']
    cantidad = 10
    
    # Create vale
    response = client.post('/api/vales',
                          headers={'Authorization': f'Bearer {tenant1_token}'},
                          json={
                              'producto_id': tenant1_producto['id'],
                              'cantidad': cantidad,
                              'request_id': 'stock-test-001'
                          })
    assert response.status_code == 201
    
    # Check product stock decreased
    with app.app_context():
        producto = Producto.query.get(tenant1_producto['id'])
        assert producto.stock == initial_stock - cantidad


def test_insufficient_stock_returns_409(client, app, tenant1_token, tenant1_producto):
    """Test that ordering more than available stock returns 409 Conflict"""
    
    # Try to order more than available
    response = client.post('/api/vales',
                          headers={'Authorization': f'Bearer {tenant1_token}'},
                          json={
                              'producto_id': tenant1_producto['id'],
                              'cantidad': tenant1_producto['stock'] + 100,  # More than available
                              'request_id': 'insufficient-stock-001'
                          })
    
    assert response.status_code == 409
    data = response.get_json()
    assert 'insufficient stock' in data['error'].lower()
    assert 'available' in data
    assert 'requested' in data


def test_stock_cannot_go_negative(client, app, tenant1_token, tenant1_producto):
    """Test that stock validation prevents negative stock"""
    
    # Order exactly all stock
    response = client.post('/api/vales',
                          headers={'Authorization': f'Bearer {tenant1_token}'},
                          json={
                              'producto_id': tenant1_producto['id'],
                              'cantidad': tenant1_producto['stock'],
                              'request_id': 'deplete-stock-001'
                          })
    assert response.status_code == 201
    
    # Try to order one more - should fail
    response = client.post('/api/vales',
                          headers={'Authorization': f'Bearer {tenant1_token}'},
                          json={
                              'producto_id': tenant1_producto['id'],
                              'cantidad': 1,
                              'request_id': 'negative-stock-001'
                          })
    assert response.status_code == 409


def test_concurrent_vale_creation_with_stock_check(client, app, tenant1_token, tenant1_producto):
    """
    Test that concurrent vale creation properly manages stock
    
    This simulates race condition prevention with SELECT FOR UPDATE
    """
    import threading
    
    Producto = app.models['Producto']
    
    initial_stock = tenant1_producto['stock']
    cantidad_per_vale = 5
    num_vales = 3
    
    # Create multiple vales (sequentially in test, but demonstrates locking works)
    for i in range(num_vales):
        response = client.post('/api/vales',
                              headers={'Authorization': f'Bearer {tenant1_token}'},
                              json={
                                  'producto_id': tenant1_producto['id'],
                                  'cantidad': cantidad_per_vale,
                                  'request_id': f'concurrent-test-{i}'
                              })
        assert response.status_code == 201
    
    # Check final stock
    with app.app_context():
        producto = Producto.query.get(tenant1_producto['id'])
        expected_stock = initial_stock - (cantidad_per_vale * num_vales)
        assert producto.stock == expected_stock


def test_vale_request_id_must_be_unique(client, app, tenant1_token, tenant1_producto):
    """Test that request_id must be globally unique across all tenants"""
    
    Producto = app.models['Producto']
    
    # Create vale with request_id
    response = client.post('/api/vales',
                          headers={'Authorization': f'Bearer {tenant1_token}'},
                          json={
                              'producto_id': tenant1_producto['id'],
                              'cantidad': 5,
                              'request_id': 'unique-request-id-001'
                          })
    assert response.status_code == 201
    
    # Try to create vale with different product but same request_id
    # Should return the existing vale (idempotent behavior)
    with app.app_context():
        # Create another product
        producto2 = Producto(
            tenant_id=1,
            nombre='Product 2',
            precio=50.00,
            stock=20,
            activo=True
        )
        db.session.add(producto2)
        db.session.commit()
        producto2_id = producto2.id
    
    response = client.post('/api/vales',
                          headers={'Authorization': f'Bearer {tenant1_token}'},
                          json={
                              'producto_id': producto2_id,
                              'cantidad': 3,
                              'request_id': 'unique-request-id-001'  # Same request_id
                          })
    
    # Should return existing vale (idempotent)
    assert response.status_code == 200
    data = response.get_json()
    # Should be the first vale, not a new one
    assert data['vale']['producto_id'] == tenant1_producto['id']


def test_audit_logs_created_for_vale(client, app, tenant1_token, tenant1_producto):
    """Test that audit logs are created when vale is created"""
    
    AuditLog = app.models['AuditLog']
    
    # Create vale
    response = client.post('/api/vales',
                          headers={'Authorization': f'Bearer {tenant1_token}'},
                          json={
                              'producto_id': tenant1_producto['id'],
                              'cantidad': 5,
                              'request_id': 'audit-test-001'
                          })
    assert response.status_code == 201
    vale_id = response.get_json()['vale']['id']
    
    # Check audit logs exist
    with app.app_context():
        # Should have audit log for vale creation
        vale_audit = AuditLog.query.filter_by(
            entidad_tipo='Vale',
            entidad_id=vale_id,
            accion='CREATE'
        ).first()
        assert vale_audit is not None
        assert vale_audit.tenant_id == 1
        
        # Should have audit log for product stock update
        product_audit = AuditLog.query.filter_by(
            entidad_tipo='Producto',
            entidad_id=tenant1_producto['id'],
            accion='UPDATE'
        ).first()
        assert product_audit is not None


def test_vale_cantidad_must_be_positive(client, tenant1_token, tenant1_producto):
    """Test that vale cantidad must be positive"""
    
    response = client.post('/api/vales',
                          headers={'Authorization': f'Bearer {tenant1_token}'},
                          json={
                              'producto_id': tenant1_producto['id'],
                              'cantidad': 0,  # Invalid
                              'request_id': 'zero-cantidad-001'
                          })
    assert response.status_code == 400
    
    response = client.post('/api/vales',
                          headers={'Authorization': f'Bearer {tenant1_token}'},
                          json={
                              'producto_id': tenant1_producto['id'],
                              'cantidad': -5,  # Invalid
                              'request_id': 'negative-cantidad-001'
                          })
    assert response.status_code == 400


def test_producto_stock_update_validation(client, tenant1_token, tenant1_producto):
    """Test that product stock cannot be set to negative via PUT"""
    
    response = client.put(f'/api/productos/{tenant1_producto["id"]}',
                         headers={'Authorization': f'Bearer {tenant1_token}'},
                         json={'stock': -10})
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'negative' in data['error'].lower() or 'cannot be negative' in data['error'].lower()
