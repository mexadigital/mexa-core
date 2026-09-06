"""
Tests for multi-tenant isolation
Ensures users from one tenant cannot access data from another tenant
"""
import pytest


def test_user_cannot_access_other_tenant_vales(client, app, tenant1_token, tenant2_token, 
                                                  tenant1_producto, tenant2_producto,
                                                  tenant1_user, tenant2_user):
    """Test that tenant1 user cannot access tenant2 vales"""
    
    # Create vale in tenant1
    response = client.post('/api/vales', 
                          headers={'Authorization': f'Bearer {tenant1_token}'},
                          json={
                              'producto_id': tenant1_producto['id'],
                              'cantidad': 5,
                              'request_id': 'test-vale-t1-001'
                          })
    assert response.status_code == 201
    vale1_id = response.get_json()['vale']['id']
    
    # Create vale in tenant2
    response = client.post('/api/vales',
                          headers={'Authorization': f'Bearer {tenant2_token}'},
                          json={
                              'producto_id': tenant2_producto['id'],
                              'cantidad': 3,
                              'request_id': 'test-vale-t2-001'
                          })
    assert response.status_code == 201
    vale2_id = response.get_json()['vale']['id']
    
    # Tenant1 user lists vales - should only see their vale
    response = client.get('/api/vales',
                         headers={'Authorization': f'Bearer {tenant1_token}'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 1
    assert data['vales'][0]['id'] == vale1_id
    
    # Tenant2 user lists vales - should only see their vale
    response = client.get('/api/vales',
                         headers={'Authorization': f'Bearer {tenant2_token}'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 1
    assert data['vales'][0]['id'] == vale2_id
    
    # Tenant1 user tries to access tenant2's vale by ID - should fail
    response = client.get(f'/api/vales/{vale2_id}',
                         headers={'Authorization': f'Bearer {tenant1_token}'})
    assert response.status_code == 404


def test_user_cannot_access_other_tenant_productos(client, tenant1_token, tenant2_token,
                                                     tenant1_producto, tenant2_producto):
    """Test that tenant1 user cannot access tenant2 productos"""
    
    # Tenant1 lists productos - should only see their product
    response = client.get('/api/productos',
                         headers={'Authorization': f'Bearer {tenant1_token}'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 1
    assert data['productos'][0]['id'] == tenant1_producto['id']
    
    # Tenant2 lists productos - should only see their product
    response = client.get('/api/productos',
                         headers={'Authorization': f'Bearer {tenant2_token}'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 1
    assert data['productos'][0]['id'] == tenant2_producto['id']
    
    # Tenant1 tries to access tenant2's product by ID - should fail
    response = client.get(f'/api/productos/{tenant2_producto["id"]}',
                         headers={'Authorization': f'Bearer {tenant1_token}'})
    assert response.status_code == 404


def test_user_cannot_create_vale_with_other_tenant_producto(client, tenant1_token, tenant2_producto):
    """Test that tenant1 user cannot create vale with tenant2's product"""
    
    response = client.post('/api/vales',
                          headers={'Authorization': f'Bearer {tenant1_token}'},
                          json={
                              'producto_id': tenant2_producto['id'],  # Different tenant's product
                              'cantidad': 5,
                              'request_id': 'test-cross-tenant-001'
                          })
    
    # Should fail because product doesn't exist in tenant1
    assert response.status_code == 404
    data = response.get_json()
    assert 'not found' in data['error'].lower() or 'not accessible' in data['error'].lower()


def test_user_cannot_update_other_tenant_producto(client, tenant1_token, tenant2_producto):
    """Test that tenant1 user cannot update tenant2's product"""
    
    response = client.put(f'/api/productos/{tenant2_producto["id"]}',
                         headers={'Authorization': f'Bearer {tenant1_token}'},
                         json={'precio': 999.99})
    
    assert response.status_code == 404


def test_user_cannot_delete_other_tenant_producto(client, tenant1_token, tenant2_producto):
    """Test that tenant1 user cannot delete tenant2's product"""
    
    response = client.delete(f'/api/productos/{tenant2_producto["id"]}',
                            headers={'Authorization': f'Bearer {tenant1_token}'})
    
    assert response.status_code == 404


def test_same_email_different_tenants(client):
    """Test that same email can exist in different tenants"""
    
    # Register same email in tenant1
    response = client.post('/api/auth/register', json={
        'email': 'shared@test.com',
        'nombre': 'User in Tenant1',
        'password': 'pass123',
        'tenant_slug': 'tenant1'
    })
    assert response.status_code == 201
    
    # Register same email in tenant2 - should succeed
    response = client.post('/api/auth/register', json={
        'email': 'shared@test.com',
        'nombre': 'User in Tenant2',
        'password': 'pass456',
        'tenant_slug': 'tenant2'
    })
    assert response.status_code == 201


def test_same_product_name_different_tenants(client, tenant1_token, tenant2_token):
    """Test that same product name can exist in different tenants"""
    
    # Create product in tenant1
    response = client.post('/api/productos',
                          headers={'Authorization': f'Bearer {tenant1_token}'},
                          json={
                              'nombre': 'Shared Product Name',
                              'precio': 100.00,
                              'stock': 10
                          })
    assert response.status_code == 201
    
    # Create product with same name in tenant2 - should succeed
    response = client.post('/api/productos',
                          headers={'Authorization': f'Bearer {tenant2_token}'},
                          json={
                              'nombre': 'Shared Product Name',
                              'precio': 200.00,
                              'stock': 20
                          })
    assert response.status_code == 201
