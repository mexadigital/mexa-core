"""
Multi-tenant routes for Mexa Core API

Implements tenant-scoped routes for:
- Authentication (login, register)
- Vales (vouchers/orders) with SELECT FOR UPDATE and idempotency
- Productos (products) with stock management
- Usuarios (users)

All routes enforce tenant isolation and include audit logging.
"""
from flask import Blueprint, request, jsonify, g, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from app.app_factory import db
from app.middleware import require_tenant_context, validate_tenant_access
from app.auth_utils import hash_password, verify_password, generate_token
from app.audit_utils import log_audit
import logging
import uuid

logger = logging.getLogger(__name__)

# Helper function to get models from current app
def get_models():
    """Get model classes from current app context"""
    models = current_app.models
    return (models['Tenant'], models['Usuario'], models['Producto'], 
            models['Vale'], models['AuditLog'])

# =============================================================================
# BLUEPRINTS
# =============================================================================

auth_bp = Blueprint('auth', __name__)
vales_bp = Blueprint('vales', __name__)
productos_bp = Blueprint('productos', __name__)
usuarios_bp = Blueprint('usuarios', __name__)


# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request Body:
        {
            "email": "user@example.com",
            "nombre": "User Name",
            "password": "securepassword",
            "tenant_slug": "default"  // optional, defaults to 'default'
        }
    """
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['email', 'nombre', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get tenant (default to 'default' tenant)
        tenant_slug = data.get('tenant_slug', 'default')
        tenant = Tenant.query.filter_by(slug=tenant_slug, activo=True).first()
        
        if not tenant:
            return jsonify({'error': 'Invalid tenant'}), 400
        
        # Check if user already exists in this tenant
        existing = Usuario.query.filter_by(
            tenant_id=tenant.id,
            email=data['email']
        ).first()
        
        if existing:
            return jsonify({'error': 'User already exists in this tenant'}), 409
        
        # Create user
        usuario = Usuario(
            tenant_id=tenant.id,
            email=data['email'],
            nombre=data['nombre'],
            password_hash=hash_password(data['password']),
            activo=True
        )
        
        db.session.add(usuario)
        db.session.commit()
        
        # Create audit log
        log_audit('CREATE', 'Usuario', usuario.id, 
                 {'email': usuario.email}, db_session=db.session)
        db.session.commit()
        
        logger.info(f"User registered: {usuario.email} in tenant {tenant.slug}")
        
        return jsonify({
            'message': 'User created successfully',
            'usuario': usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login - returns JWT token with tenant_id
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "securepassword",
            "tenant_slug": "default"  // optional, defaults to 'default'
        }
    
    Response:
        {
            "access_token": "eyJ...",
            "usuario": {...}
        }
    """
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Missing email or password'}), 400
        
        # Get tenant (default to 'default' tenant)
        tenant_slug = data.get('tenant_slug', 'default')
        tenant = Tenant.query.filter_by(slug=tenant_slug, activo=True).first()
        
        if not tenant:
            return jsonify({'error': 'Invalid tenant'}), 400
        
        # Find user in tenant
        usuario = Usuario.query.filter_by(
            tenant_id=tenant.id,
            email=data['email'],
            activo=True
        ).first()
        
        if not usuario:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not verify_password(data['password'], usuario.password_hash):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token with tenant_id in claims
        access_token = generate_token(usuario.id, tenant.id, usuario.email)
        
        # Create audit log
        log_audit('LOGIN', 'Usuario', usuario.id, None, db_session=db.session)
        db.session.commit()
        
        logger.info(f"User logged in: {usuario.email} in tenant {tenant.slug}")
        
        return jsonify({
            'access_token': access_token,
            'usuario': usuario.to_dict(include_tenant=True)
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


# =============================================================================
# VALES ROUTES (with SELECT FOR UPDATE and idempotency)
# =============================================================================

@vales_bp.route('', methods=['POST'])
@require_tenant_context
def create_vale():
    """
    Create a new vale with idempotency support and SELECT FOR UPDATE for stock management
    
    Request Body:
        {
            "producto_id": 1,
            "cantidad": 5,
            "comentario": "Order notes",
            "request_id": "unique-request-id"  // Required for idempotency
        }
    
    Features:
    - Idempotency: Same request_id returns same result (409 if exists)
    - Stock management: Uses SELECT FOR UPDATE to prevent race conditions
    - Stock validation: Returns 409 if insufficient stock
    - Audit logging: All operations logged
    - Tenant isolation: Only access products in same tenant
    """
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        data = request.get_json()
        tenant_id = g.tenant_id
        usuario_id = g.usuario_id
        
        # Validate required fields
        if not all(k in data for k in ['producto_id', 'cantidad', 'request_id']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        request_id = data['request_id']
        producto_id = data['producto_id']
        cantidad = data['cantidad']
        
        # Validate cantidad
        if cantidad <= 0:
            return jsonify({'error': 'Cantidad must be positive'}), 400
        
        # Check for idempotency - if request_id already exists, return existing vale
        existing_vale = Vale.query.filter_by(request_id=request_id).first()
        if existing_vale:
            logger.info(f"Idempotent request detected: request_id={request_id}")
            
            # Validate tenant access
            if not validate_tenant_access(existing_vale):
                return jsonify({'error': 'Access denied'}), 403
            
            return jsonify({
                'message': 'Vale already exists (idempotent)',
                'vale': existing_vale.to_dict(include_relations=True)
            }), 200
        
        # Begin transaction with SELECT FOR UPDATE
        with db.session.begin_nested():
            # Lock producto row for update (prevents concurrent stock modifications)
            producto = db.session.query(Producto).filter(
                and_(
                    Producto.id == producto_id,
                    Producto.tenant_id == tenant_id,
                    Producto.activo == True
                )
            ).with_for_update().first()
            
            if not producto:
                return jsonify({'error': 'Product not found or not accessible'}), 404
            
            # Validate sufficient stock
            if producto.stock < cantidad:
                return jsonify({
                    'error': 'Insufficient stock',
                    'available': producto.stock,
                    'requested': cantidad
                }), 409
            
            # Calculate total amount
            monto_total = producto.precio * cantidad
            
            # Create vale
            vale = Vale(
                tenant_id=tenant_id,
                usuario_id=usuario_id,
                producto_id=producto_id,
                request_id=request_id,
                cantidad=cantidad,
                monto_total=monto_total,
                estado='pendiente',
                comentario=data.get('comentario')
            )
            
            # Update product stock
            producto.stock -= cantidad
            
            db.session.add(vale)
            db.session.flush()  # Get vale.id before commit
            
            # Create audit logs
            log_audit('CREATE', 'Vale', vale.id,
                     {'producto_id': producto_id, 'cantidad': cantidad, 'request_id': request_id},
                     db_session=db.session)
            log_audit('UPDATE', 'Producto', producto_id,
                     {'action': 'stock_decrease', 'cantidad': cantidad, 'new_stock': producto.stock},
                     db_session=db.session)
        
        # Commit transaction
        db.session.commit()
        
        # Refresh to get relationships
        db.session.refresh(vale)
        
        logger.info(f"Vale created: id={vale.id}, tenant={tenant_id}, request_id={request_id}")
        
        return jsonify({
            'message': 'Vale created successfully',
            'vale': vale.to_dict(include_relations=True)
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Vale creation integrity error: {str(e)}")
        # Check if it's duplicate request_id
        if 'request_id' in str(e):
            return jsonify({'error': 'Duplicate request_id'}), 409
        return jsonify({'error': 'Database integrity error'}), 409
    except Exception as e:
        db.session.rollback()
        logger.error(f"Vale creation error: {str(e)}")
        return jsonify({'error': 'Failed to create vale'}), 500


@vales_bp.route('', methods=['GET'])
@require_tenant_context
def list_vales():
    """
    List all vales for current tenant
    
    Query Parameters:
        - estado: Filter by estado (pendiente, completado, cancelado)
        - limit: Max results (default: 100)
        - offset: Pagination offset (default: 0)
    """
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        tenant_id = g.tenant_id
        
        # Build query
        query = Vale.query.filter_by(tenant_id=tenant_id)
        
        # Apply filters
        estado = request.args.get('estado')
        if estado:
            query = query.filter_by(estado=estado)
        
        # Pagination
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = int(request.args.get('offset', 0))
        
        # Execute query
        vales = query.order_by(Vale.created_at.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'vales': [v.to_dict(include_relations=True) for v in vales],
            'count': len(vales),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"List vales error: {str(e)}")
        return jsonify({'error': 'Failed to list vales'}), 500


@vales_bp.route('/<int:vale_id>', methods=['GET'])
@require_tenant_context
def get_vale(vale_id):
    """Get a single vale by ID (tenant-scoped)"""
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        tenant_id = g.tenant_id
        
        vale = Vale.query.filter_by(id=vale_id, tenant_id=tenant_id).first()
        
        if not vale:
            return jsonify({'error': 'Vale not found'}), 404
        
        return jsonify({'vale': vale.to_dict(include_relations=True)}), 200
        
    except Exception as e:
        logger.error(f"Get vale error: {str(e)}")
        return jsonify({'error': 'Failed to get vale'}), 500


@vales_bp.route('/<int:vale_id>', methods=['PUT'])
@require_tenant_context
def update_vale(vale_id):
    """
    Update vale status (tenant-scoped)
    
    Request Body:
        {
            "estado": "completado",  // pendiente, completado, cancelado
            "comentario": "Updated notes"
        }
    """
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        tenant_id = g.tenant_id
        data = request.get_json()
        
        # Get vale (verify tenant access)
        vale = Vale.query.filter_by(id=vale_id, tenant_id=tenant_id).first()
        
        if not vale:
            return jsonify({'error': 'Vale not found'}), 404
        
        # Update fields
        if 'estado' in data:
            vale.estado = data['estado']
        if 'comentario' in data:
            vale.comentario = data['comentario']
        
        # Audit log
        log_audit('UPDATE', 'Vale', vale_id, data, db_session=db.session)
        
        db.session.commit()
        
        logger.info(f"Vale updated: id={vale_id}, tenant={tenant_id}")
        
        return jsonify({
            'message': 'Vale updated successfully',
            'vale': vale.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update vale error: {str(e)}")
        return jsonify({'error': 'Failed to update vale'}), 500


@vales_bp.route('/<int:vale_id>', methods=['DELETE'])
@require_tenant_context
def delete_vale(vale_id):
    """Delete vale (tenant-scoped) - soft delete by setting estado to 'cancelado'"""
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        tenant_id = g.tenant_id
        
        # Get vale (verify tenant access)
        vale = Vale.query.filter_by(id=vale_id, tenant_id=tenant_id).first()
        
        if not vale:
            return jsonify({'error': 'Vale not found'}), 404
        
        # Soft delete - change status to cancelado
        vale.estado = 'cancelado'
        
        # Audit log
        log_audit('DELETE', 'Vale', vale_id, None, db_session=db.session)
        
        db.session.commit()
        
        logger.info(f"Vale deleted (soft): id={vale_id}, tenant={tenant_id}")
        
        return jsonify({'message': 'Vale deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete vale error: {str(e)}")
        return jsonify({'error': 'Failed to delete vale'}), 500


# =============================================================================
# PRODUCTOS ROUTES
# =============================================================================

@productos_bp.route('', methods=['POST'])
@require_tenant_context
def create_producto():
    """
    Create a new product (tenant-scoped)
    
    Request Body:
        {
            "nombre": "Product Name",
            "descripcion": "Product description",
            "sku": "SKU-001",
            "precio": 100.50,
            "stock": 10
        }
    """
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        data = request.get_json()
        tenant_id = g.tenant_id
        
        # Validate required fields
        if not all(k in data for k in ['nombre', 'precio']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create product
        producto = Producto(
            tenant_id=tenant_id,
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            sku=data.get('sku'),
            precio=data['precio'],
            stock=data.get('stock', 0),
            activo=True
        )
        
        db.session.add(producto)
        db.session.flush()
        
        # Audit log
        log_audit('CREATE', 'Producto', producto.id, data, db_session=db.session)
        
        db.session.commit()
        
        logger.info(f"Product created: id={producto.id}, tenant={tenant_id}")
        
        return jsonify({
            'message': 'Product created successfully',
            'producto': producto.to_dict()
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Product creation integrity error: {str(e)}")
        if 'nombre' in str(e):
            return jsonify({'error': 'Product with this name already exists in tenant'}), 409
        return jsonify({'error': 'Database integrity error'}), 409
    except Exception as e:
        db.session.rollback()
        logger.error(f"Product creation error: {str(e)}")
        return jsonify({'error': 'Failed to create product'}), 500


@productos_bp.route('', methods=['GET'])
@require_tenant_context
def list_productos():
    """List all products for current tenant"""
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        tenant_id = g.tenant_id
        
        # Build query
        query = Producto.query.filter_by(tenant_id=tenant_id, activo=True)
        
        # Pagination
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = int(request.args.get('offset', 0))
        
        # Execute query
        productos = query.order_by(Producto.nombre).limit(limit).offset(offset).all()
        
        return jsonify({
            'productos': [p.to_dict() for p in productos],
            'count': len(productos)
        }), 200
        
    except Exception as e:
        logger.error(f"List productos error: {str(e)}")
        return jsonify({'error': 'Failed to list productos'}), 500


@productos_bp.route('/<int:producto_id>', methods=['GET'])
@require_tenant_context
def get_producto(producto_id):
    """Get a single product by ID (tenant-scoped)"""
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        tenant_id = g.tenant_id
        
        producto = Producto.query.filter_by(id=producto_id, tenant_id=tenant_id).first()
        
        if not producto:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({'producto': producto.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Get producto error: {str(e)}")
        return jsonify({'error': 'Failed to get product'}), 500


@productos_bp.route('/<int:producto_id>', methods=['PUT'])
@require_tenant_context
def update_producto(producto_id):
    """Update product (tenant-scoped)"""
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        tenant_id = g.tenant_id
        data = request.get_json()
        
        # Get producto (verify tenant access)
        producto = Producto.query.filter_by(id=producto_id, tenant_id=tenant_id).first()
        
        if not producto:
            return jsonify({'error': 'Product not found'}), 404
        
        # Update fields
        if 'nombre' in data:
            producto.nombre = data['nombre']
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        if 'sku' in data:
            producto.sku = data['sku']
        if 'precio' in data:
            producto.precio = data['precio']
        if 'stock' in data:
            # Validate stock is non-negative
            if data['stock'] < 0:
                return jsonify({'error': 'Stock cannot be negative'}), 400
            producto.stock = data['stock']
        if 'activo' in data:
            producto.activo = data['activo']
        
        # Audit log
        log_audit('UPDATE', 'Producto', producto_id, data, db_session=db.session)
        
        db.session.commit()
        
        logger.info(f"Product updated: id={producto_id}, tenant={tenant_id}")
        
        return jsonify({
            'message': 'Product updated successfully',
            'producto': producto.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update producto error: {str(e)}")
        return jsonify({'error': 'Failed to update product'}), 500


@productos_bp.route('/<int:producto_id>', methods=['DELETE'])
@require_tenant_context
def delete_producto(producto_id):
    """Delete product (tenant-scoped) - soft delete"""
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        tenant_id = g.tenant_id
        
        # Get producto (verify tenant access)
        producto = Producto.query.filter_by(id=producto_id, tenant_id=tenant_id).first()
        
        if not producto:
            return jsonify({'error': 'Product not found'}), 404
        
        # Soft delete
        producto.activo = False
        
        # Audit log
        log_audit('DELETE', 'Producto', producto_id, None, db_session=db.session)
        
        db.session.commit()
        
        logger.info(f"Product deleted (soft): id={producto_id}, tenant={tenant_id}")
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete producto error: {str(e)}")
        return jsonify({'error': 'Failed to delete product'}), 500


# =============================================================================
# USUARIOS ROUTES
# =============================================================================

@usuarios_bp.route('', methods=['GET'])
@require_tenant_context
def list_usuarios():
    """List all users for current tenant"""
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        tenant_id = g.tenant_id
        
        usuarios = Usuario.query.filter_by(tenant_id=tenant_id, activo=True).all()
        
        return jsonify({
            'usuarios': [u.to_dict() for u in usuarios],
            'count': len(usuarios)
        }), 200
        
    except Exception as e:
        logger.error(f"List usuarios error: {str(e)}")
        return jsonify({'error': 'Failed to list users'}), 500


@usuarios_bp.route('/<int:usuario_id>', methods=['GET'])
@require_tenant_context
def get_usuario(usuario_id):
    """Get a single user by ID (tenant-scoped)"""
    Tenant, Usuario, Producto, Vale, AuditLog = get_models()
    try:
        tenant_id = g.tenant_id
        
        usuario = Usuario.query.filter_by(id=usuario_id, tenant_id=tenant_id).first()
        
        if not usuario:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'usuario': usuario.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Get usuario error: {str(e)}")
        return jsonify({'error': 'Failed to get user'}), 500
