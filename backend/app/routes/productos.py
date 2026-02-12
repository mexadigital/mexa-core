from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.producto import Producto
from app.models.usuario import Usuario

bp = Blueprint('productos', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_productos():
    """Get all active products"""
    productos = Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()
    return jsonify([producto.to_dict() for producto in productos]), 200


@bp.route('/<int:producto_id>', methods=['GET'])
@jwt_required()
def get_producto(producto_id):
    """Get a single product by ID"""
    producto = Producto.query.get(producto_id)
    
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    return jsonify(producto.to_dict()), 200


@bp.route('/', methods=['POST'])
@jwt_required()
def create_producto():
    """Create a new product (admin only)"""
    user_id = get_jwt_identity()
    user = Usuario.query.get(user_id)
    
    if user.rol != 'admin':
        return jsonify({'error': 'Solo administradores pueden crear productos'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('nombre'):
        return jsonify({'error': 'Nombre del producto es requerido'}), 400
    
    # Check if product already exists
    if Producto.query.filter_by(nombre=data['nombre']).first():
        return jsonify({'error': 'Ya existe un producto con ese nombre'}), 400
    
    producto = Producto(
        nombre=data['nombre'],
        descripcion=data.get('descripcion'),
        categoria=data.get('categoria'),
        unidad_medida=data.get('unidad_medida', 'unidad'),
        stock_minimo=data.get('stock_minimo', 10)
    )
    
    db.session.add(producto)
    db.session.commit()
    
    return jsonify({
        'message': 'Producto creado exitosamente',
        'producto': producto.to_dict()
    }), 201


@bp.route('/<int:producto_id>', methods=['PUT'])
@jwt_required()
def update_producto(producto_id):
    """Update a product (admin only)"""
    user_id = get_jwt_identity()
    user = Usuario.query.get(user_id)
    
    if user.rol != 'admin':
        return jsonify({'error': 'Solo administradores pueden actualizar productos'}), 403
    
    producto = Producto.query.get(producto_id)
    
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    data = request.get_json()
    
    if 'nombre' in data:
        # Check if new name conflicts with existing product
        existing = Producto.query.filter_by(nombre=data['nombre']).first()
        if existing and existing.id != producto_id:
            return jsonify({'error': 'Ya existe un producto con ese nombre'}), 400
        producto.nombre = data['nombre']
    
    if 'descripcion' in data:
        producto.descripcion = data['descripcion']
    
    if 'categoria' in data:
        producto.categoria = data['categoria']
    
    if 'unidad_medida' in data:
        producto.unidad_medida = data['unidad_medida']
    
    if 'stock_minimo' in data:
        try:
            stock_minimo = int(data['stock_minimo'])
            if stock_minimo < 0:
                return jsonify({'error': 'Stock mínimo debe ser positivo'}), 400
            producto.stock_minimo = stock_minimo
        except (ValueError, TypeError):
            return jsonify({'error': 'Stock mínimo debe ser un número entero'}), 400
    
    if 'activo' in data:
        producto.activo = bool(data['activo'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Producto actualizado exitosamente',
        'producto': producto.to_dict()
    }), 200


@bp.route('/<int:producto_id>', methods=['DELETE'])
@jwt_required()
def delete_producto(producto_id):
    """Soft delete a product (admin only)"""
    user_id = get_jwt_identity()
    user = Usuario.query.get(user_id)
    
    if user.rol != 'admin':
        return jsonify({'error': 'Solo administradores pueden eliminar productos'}), 403
    
    producto = Producto.query.get(producto_id)
    
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    # Soft delete - just set activo to False
    producto.activo = False
    db.session.commit()
    
    return jsonify({'message': 'Producto eliminado exitosamente'}), 200
