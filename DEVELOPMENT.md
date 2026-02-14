# Development Guide - Mexa Core Multi-Tenant System

## Overview

Mexa Core is a multi-tenant Flask application that provides secure, isolated environments for multiple organizations. Each tenant has their own isolated data while sharing the same application infrastructure.

## Multi-Tenant Architecture

### Key Concepts

**Tenant Isolation**: All data is strictly scoped to tenants. Users in one tenant cannot access or modify data from another tenant.

**Default Tenant**: The system includes a default tenant (ID=1, slug='default') created automatically on first run. This tenant is used for:
- Initial user registration
- System-level operations
- Migration backfill operations

### Database Schema

#### Core Tables

1. **tenants**: Organization/tenant information
   - `id`: Unique identifier
   - `slug`: URL-friendly unique identifier
   - `nombre`: Organization name
   - `email`: Contact email
   - `plan`: Subscription plan (basic, pro, enterprise)
   - `activo`: Active status

2. **usuarios**: Users scoped to tenants
   - `tenant_id`: Foreign key to tenants (NOT NULL, NO CASCADE)
   - Unique constraint: `(tenant_id, email)` - same email can exist in different tenants

3. **productos**: Products scoped to tenants
   - `tenant_id`: Foreign key to tenants (NOT NULL, NO CASCADE)
   - `stock`: Managed with SELECT FOR UPDATE for race condition prevention
   - Unique constraint: `(tenant_id, nombre)` - product names unique per tenant
   - Check constraint: `stock >= 0` - prevents negative stock

4. **vales**: Orders/vouchers scoped to tenants
   - `tenant_id`: Foreign key to tenants (NOT NULL, NO CASCADE)
   - `request_id`: Unique identifier for idempotency (prevents duplicate orders)
   - Uses SELECT FOR UPDATE when modifying product stock

5. **audit_logs**: Complete audit trail with tenant context
   - `tenant_id`: Foreign key to tenants (NOT NULL, NO CASCADE)
   - Tracks all CRUD operations
   - Includes IP address and user agent

### Safety Features

#### 1. SELECT FOR UPDATE (Stock Management)

When creating a vale (order), the system uses database row locking to prevent race conditions:

```python
# Lock product row for update
producto = db.session.query(Producto).filter(
    Producto.id == producto_id,
    Producto.tenant_id == tenant_id
).with_for_update().first()

# Validate stock
if producto.stock < cantidad:
    return error('Insufficient stock')

# Update stock atomically
producto.stock -= cantidad
```

**Benefits**:
- Prevents overselling (multiple simultaneous orders)
- Ensures stock never goes negative
- Maintains data consistency under high concurrency

#### 2. Idempotency (request_id)

Every vale creation requires a unique `request_id`. If the same `request_id` is submitted multiple times:
- First request: Creates the vale
- Subsequent requests: Returns the existing vale (HTTP 200)

```python
# Check for existing vale with same request_id
existing_vale = Vale.query.filter_by(request_id=request_id).first()
if existing_vale:
    return existing_vale  # Idempotent response
```

**Benefits**:
- Prevents duplicate orders on network retries
- Safe to retry failed requests
- Consistent behavior for clients

#### 3. Transaction Safety

All operations that modify multiple tables use nested transactions:

```python
with db.session.begin_nested():
    # Create vale
    # Update product stock
    # Create audit logs
# Commit all or rollback all
db.session.commit()
```

#### 4. No CASCADE Deletes

Foreign keys to tenants do NOT use `ondelete='CASCADE'`. This prevents:
- Accidental mass data deletion
- Cascade effects from tenant deletion
- Data loss from administrative errors

**Manual cleanup is required** if a tenant needs to be deleted.

## Authentication & JWT

### JWT Token Structure

When a user logs in, they receive a JWT token with:

```json
{
  "identity": <usuario_id>,
  "tenant_id": <tenant_id>,
  "email": "user@example.com",
  "exp": <expiration_timestamp>
}
```

### Middleware: require_tenant_context

All protected endpoints use the `@require_tenant_context` decorator:

```python
@vales_bp.route('', methods=['POST'])
@require_tenant_context
def create_vale():
    tenant_id = g.tenant_id  # Extracted from JWT
    # ... endpoint logic
```

**What it does**:
1. Verifies JWT token is present and valid
2. Extracts `tenant_id` from token claims
3. Stores `tenant_id` in Flask's `g` object
4. Validates user belongs to the tenant
5. Returns 401 if token is missing/invalid

### Request Flow

```
1. Client sends request with JWT token in Authorization header
   Authorization: Bearer <jwt_token>

2. @require_tenant_context decorator:
   - Validates token
   - Extracts tenant_id from claims
   - Stores in g.tenant_id

3. Route handler:
   - Uses g.tenant_id to filter queries
   - Ensures all operations are tenant-scoped

4. Response sent back to client
```

## API Endpoints

### Authentication

#### POST /api/auth/register
Register a new user.

**Request**:
```json
{
  "email": "user@example.com",
  "nombre": "John Doe",
  "password": "securepassword",
  "tenant_slug": "default"
}
```

**Response** (201):
```json
{
  "message": "User created successfully",
  "usuario": {
    "id": 1,
    "tenant_id": 1,
    "email": "user@example.com",
    "nombre": "John Doe",
    "activo": true
  }
}
```

#### POST /api/auth/login
Login and receive JWT token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "tenant_slug": "default"
}
```

**Response** (200):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "usuario": {
    "id": 1,
    "tenant_id": 1,
    "email": "user@example.com",
    "nombre": "John Doe"
  }
}
```

### Vales (Orders/Vouchers)

All vale endpoints require authentication and enforce tenant isolation.

#### POST /api/vales
Create a new vale (order).

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Request**:
```json
{
  "producto_id": 5,
  "cantidad": 3,
  "request_id": "order-123-456",
  "comentario": "Urgent order"
}
```

**Response** (201):
```json
{
  "message": "Vale created successfully",
  "vale": {
    "id": 10,
    "tenant_id": 1,
    "producto_id": 5,
    "cantidad": 3,
    "monto_total": 150.00,
    "estado": "pendiente",
    "request_id": "order-123-456"
  }
}
```

**Error Responses**:
- 400: Missing required fields or invalid data
- 401: Invalid or missing JWT token
- 404: Product not found or not accessible
- 409: Insufficient stock OR duplicate request_id

#### GET /api/vales
List all vales for current tenant.

**Query Parameters**:
- `estado`: Filter by status (pendiente, completado, cancelado)
- `limit`: Max results (default: 100, max: 1000)
- `offset`: Pagination offset (default: 0)

#### GET /api/vales/:id
Get a single vale by ID (tenant-scoped).

#### PUT /api/vales/:id
Update vale status.

**Request**:
```json
{
  "estado": "completado",
  "comentario": "Updated notes"
}
```

#### DELETE /api/vales/:id
Soft delete vale (sets estado to 'cancelado').

### Productos (Products)

#### POST /api/productos
Create a new product.

**Request**:
```json
{
  "nombre": "Laptop Dell XPS 15",
  "descripcion": "High-performance laptop",
  "sku": "DELL-XPS-15",
  "precio": 1299.99,
  "stock": 10
}
```

#### GET /api/productos
List all products for current tenant.

#### GET /api/productos/:id
Get a single product by ID.

#### PUT /api/productos/:id
Update product details.

#### DELETE /api/productos/:id
Soft delete product (sets activo to false).

### Usuarios (Users)

#### GET /api/usuarios
List all users in current tenant.

#### GET /api/usuarios/:id
Get a single user by ID (tenant-scoped).

## Tenant Isolation Mechanisms

### Query Filtering

**Every query MUST filter by tenant_id**:

```python
# ✅ CORRECT - Tenant-scoped
productos = Producto.query.filter_by(tenant_id=tenant_id).all()

# ❌ WRONG - No tenant filtering (cross-tenant access)
productos = Producto.query.all()
```

### Create Operations

**Every create operation MUST set tenant_id**:

```python
# ✅ CORRECT
producto = Producto(
    tenant_id=g.tenant_id,  # From JWT token
    nombre=data['nombre'],
    precio=data['precio']
)
```

### Cross-Tenant Access Prevention

The `validate_tenant_access()` function ensures entities belong to current tenant:

```python
vale = Vale.query.filter_by(id=vale_id).first()
if not validate_tenant_access(vale):
    return error('Access denied'), 403
```

## Audit Logging

All operations are logged in the `audit_logs` table:

```python
log_audit(
    accion='CREATE',
    entidad_tipo='Vale',
    entidad_id=vale.id,
    detalles={'producto_id': 5, 'cantidad': 3},
    db_session=db.session
)
```

**Logged Information**:
- tenant_id: Which tenant performed the action
- usuario_id: Which user performed the action
- accion: Action type (CREATE, UPDATE, DELETE, LOGIN)
- entidad_tipo: Type of entity affected
- entidad_id: ID of affected entity
- detalles: JSON details about the change
- ip_address: Client IP address
- user_agent: Client user agent
- created_at: Timestamp

## Development Setup

### Requirements

```bash
pip install -r requirements-multitenant.txt
```

### Environment Variables

Create a `.env` file:

```bash
# Database
DATABASE_URL=sqlite:///data/app.db
DB_DIR=data

# JWT
JWT_SECRET_KEY=your-secret-key-here

# Application
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your-app-secret-key
```

### Running the Application

```bash
# Run Flask development server
python run_multitenant.py

# Or using Flask CLI
export FLASK_APP=run_multitenant.py
flask run --port 5000
```

### Database Initialization

The application automatically:
1. Creates all tables on first run
2. Creates the default tenant (id=1, slug='default')

## Testing

### Manual Testing with curl

#### 1. Register a user
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "nombre": "Test User",
    "password": "password123",
    "tenant_slug": "default"
  }'
```

#### 2. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "tenant_slug": "default"
  }'
```

Save the `access_token` from the response.

#### 3. Create a product
```bash
curl -X POST http://localhost:5000/api/productos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "nombre": "Test Product",
    "precio": 99.99,
    "stock": 100
  }'
```

#### 4. Create a vale (order)
```bash
curl -X POST http://localhost:5000/api/vales \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "producto_id": 1,
    "cantidad": 5,
    "request_id": "test-order-001",
    "comentario": "Test order"
  }'
```

### Testing Idempotency

Submit the same request_id twice:

```bash
# First request - creates vale
curl -X POST http://localhost:5000/api/vales \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"producto_id":1,"cantidad":5,"request_id":"idempotent-123"}'

# Second request - returns existing vale (no duplicate)
curl -X POST http://localhost:5000/api/vales \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"producto_id":1,"cantidad":5,"request_id":"idempotent-123"}'
```

### Testing Stock Management

Try to order more than available stock:

```bash
# Assuming product has stock=10
curl -X POST http://localhost:5000/api/vales \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"producto_id":1,"cantidad":20,"request_id":"over-stock-001"}'

# Response: 409 Conflict
{
  "error": "Insufficient stock",
  "available": 10,
  "requested": 20
}
```

## Security Considerations

### 1. JWT Secret
Always use a strong, random secret in production:
```bash
JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
```

### 2. Password Hashing
Passwords are hashed using bcrypt (from passlib). Never store plain text passwords.

### 3. Tenant Isolation
- All queries filtered by tenant_id
- JWT tokens include tenant_id
- No cross-tenant access possible
- Foreign keys do NOT cascade delete

### 4. SQL Injection Protection
- SQLAlchemy ORM used throughout
- Parameterized queries for raw SQL
- Input validation on all endpoints

### 5. Audit Trail
- All operations logged with tenant context
- IP address and user agent tracked
- Immutable audit log (no updates/deletes)

## Migration Guide

### Adding Multi-Tenant Support to Existing Tables

If you have existing tables that need tenant support:

1. Add tenant_id column (nullable)
2. Backfill with default tenant (ID=1)
3. Make tenant_id NOT NULL
4. Add foreign key constraint (NO CASCADE)
5. Add indexes
6. Update unique constraints to include tenant_id

See `migrations/versions/005_add_multi_tenant.py` for reference.

## Troubleshooting

### Issue: "Token missing tenant context"
**Cause**: JWT token doesn't have tenant_id claim  
**Solution**: Re-login to get a new token with tenant_id

### Issue: "Access denied" (403)
**Cause**: Trying to access resource from different tenant  
**Solution**: Ensure you're accessing resources from your own tenant

### Issue: "Insufficient stock" (409)
**Cause**: Product stock is less than requested quantity  
**Solution**: Check product stock before ordering, or order smaller quantity

### Issue: "Duplicate request_id" (409)
**Cause**: Vale with same request_id already exists  
**Solution**: Use a different request_id, or check if original request succeeded

## Production Deployment

### Checklist

- [ ] Set strong JWT_SECRET_KEY
- [ ] Set strong SECRET_KEY
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Set DEBUG=False
- [ ] Configure proper logging
- [ ] Set up database backups
- [ ] Monitor audit logs
- [ ] Set up rate limiting
- [ ] Configure CORS if needed
- [ ] Use a WSGI server (gunicorn, uwsgi)

### Example Production Config

```python
# config.py - Production
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # Must be set
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set
```

### Running with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run_multitenant:app
```

## References

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Flask-JWT-Extended: https://flask-jwt-extended.readthedocs.io/
- Multi-Tenancy Patterns: https://docs.microsoft.com/en-us/azure/architecture/patterns/

## Support

For issues or questions, please open an issue on GitHub or contact the development team.
