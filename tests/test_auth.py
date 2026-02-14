"""
Tests for authentication and JWT functionality
"""
import pytest
from flask_jwt_extended import decode_token


def test_register_user(client):
    """Test user registration"""
    response = client.post('/api/auth/register', json={
        'email': 'newuser@test.com',
        'nombre': 'New User',
        'password': 'testpass123',
        'tenant_slug': 'tenant1'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'User created successfully'
    assert data['usuario']['email'] == 'newuser@test.com'
    assert data['usuario']['tenant_id'] == 1


def test_register_duplicate_user(client, tenant1_user):
    """Test registering duplicate user in same tenant fails"""
    response = client.post('/api/auth/register', json={
        'email': tenant1_user['email'],
        'nombre': 'Duplicate User',
        'password': 'testpass123',
        'tenant_slug': 'tenant1'
    })
    
    assert response.status_code == 409
    data = response.get_json()
    assert 'already exists' in data['error']


def test_login_success(client, tenant1_user):
    """Test successful login"""
    response = client.post('/api/auth/login', json={
        'email': tenant1_user['email'],
        'password': tenant1_user['password'],
        'tenant_slug': 'tenant1'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert data['usuario']['email'] == tenant1_user['email']


def test_login_wrong_password(client, tenant1_user):
    """Test login with wrong password"""
    response = client.post('/api/auth/login', json={
        'email': tenant1_user['email'],
        'password': 'wrongpassword',
        'tenant_slug': 'tenant1'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'Invalid credentials' in data['error']


def test_login_wrong_tenant(client, tenant1_user):
    """Test login with wrong tenant"""
    response = client.post('/api/auth/login', json={
        'email': tenant1_user['email'],
        'password': tenant1_user['password'],
        'tenant_slug': 'tenant2'  # Wrong tenant
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'Invalid credentials' in data['error']


def test_jwt_includes_tenant_id(client, tenant1_user, app):
    """Test that JWT token includes tenant_id"""
    response = client.post('/api/auth/login', json={
        'email': tenant1_user['email'],
        'password': tenant1_user['password'],
        'tenant_slug': 'tenant1'
    })
    
    data = response.get_json()
    token = data['access_token']
    
    # Decode token (without verification for testing)
    with app.app_context():
        decoded = decode_token(token)
        assert 'tenant_id' in decoded
        assert decoded['tenant_id'] == 1
        assert decoded['sub'] == tenant1_user['id']


def test_protected_endpoint_requires_token(client):
    """Test that protected endpoints require JWT token"""
    response = client.get('/api/vales')
    
    assert response.status_code == 401


def test_protected_endpoint_with_invalid_token(client):
    """Test protected endpoint with invalid token"""
    headers = {'Authorization': 'Bearer invalid-token'}
    response = client.get('/api/vales', headers=headers)
    
    assert response.status_code == 422  # JWT decode error
