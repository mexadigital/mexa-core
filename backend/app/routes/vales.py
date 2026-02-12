from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.vale import Vale
from app.models.producto import Producto
from app.models.usuario import Usuario
from datetime import datetime, date

bp = Blueprint('vales', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_vales():
    """Get all vales with optional filters"""
    # Query parameters for filtering
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    disciplina = request.args.get('disciplina')
    satelite = request.args.get('satelite')
    producto_id = request.args.get('producto_id')
    
    # Build query
    query = Vale.query
    
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            query = query.filter(Vale.fecha >= fecha_inicio_dt)
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido para fecha_inicio (use YYYY-MM-DD)'}), 400
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            query = query.filter(Vale.fecha <= fecha_fin_dt)
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido para fecha_fin (use YYYY-MM-DD)'}), 400
    
    if disciplina:
        query = query.filter(Vale.disciplina == disciplina)
    
    if satelite:
        query = query.filter(Vale.satelite == satelite)
    
    if producto_id:
        query = query.filter(Vale.producto_id == producto_id)
    
    # Order by most recent first
    vales = query.order_by(Vale.fecha.desc(), Vale.created_at.desc()).all()
    
    return jsonify([vale.to_dict() for vale in vales]), 200


@bp.route('/<int:vale_id>', methods=['GET'])
@jwt_required()
def get_vale(vale_id):
    """Get a single vale by ID"""
    vale = Vale.query.get(vale_id)
    
    if not vale:
        return jsonify({'error': 'Vale no encontrado'}), 404
    
    return jsonify(vale.to_dict()), 200


@bp.route('/', methods=['POST'])
@jwt_required()
def create_vale():
    """Create a new vale"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['producto_id', 'disciplina', 'satelite', 'cantidad_salida', 'stock_actual']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    # Validate disciplina
    disciplinas_validas = ['Civil', 'Mecánica', 'Eléctrica']
    if data['disciplina'] not in disciplinas_validas:
        return jsonify({'error': f'Disciplina debe ser una de: {", ".join(disciplinas_validas)}'}), 400
    
    # Validate satelite
    satelites_validos = ['#1', '#2', '#3']
    if data['satelite'] not in satelites_validos:
        return jsonify({'error': f'Satélite debe ser uno de: {", ".join(satelites_validos)}'}), 400
    
    # Validate producto exists
    producto = Producto.query.get(data['producto_id'])
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    # Validate numeric values
    try:
        cantidad_salida = int(data['cantidad_salida'])
        stock_actual = int(data['stock_actual'])
        
        if cantidad_salida < 0 or stock_actual < 0:
            return jsonify({'error': 'Cantidad y stock deben ser valores positivos'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Cantidad y stock deben ser números enteros'}), 400
    
    # Parse fecha if provided
    fecha = None
    if data.get('fecha'):
        try:
            fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido (use YYYY-MM-DD)'}), 400
    
    # Create vale
    vale = Vale(
        usuario_id=user_id,
        producto_id=data['producto_id'],
        disciplina=data['disciplina'],
        satelite=data['satelite'],
        cantidad_salida=cantidad_salida,
        stock_actual=stock_actual,
        observaciones=data.get('observaciones'),
        fecha=fecha
    )
    
    db.session.add(vale)
    db.session.commit()
    
    return jsonify({
        'message': 'Vale creado exitosamente',
        'vale': vale.to_dict()
    }), 201


@bp.route('/<int:vale_id>', methods=['PUT'])
@jwt_required()
def update_vale(vale_id):
    """Update an existing vale"""
    user_id = get_jwt_identity()
    vale = Vale.query.get(vale_id)
    
    if not vale:
        return jsonify({'error': 'Vale no encontrado'}), 404
    
    # Check if user is owner or admin
    user = Usuario.query.get(user_id)
    if vale.usuario_id != user_id and user.rol != 'admin':
        return jsonify({'error': 'No tiene permisos para modificar este vale'}), 403
    
    data = request.get_json()
    
    # Update fields if provided
    if 'disciplina' in data:
        disciplinas_validas = ['Civil', 'Mecánica', 'Eléctrica']
        if data['disciplina'] not in disciplinas_validas:
            return jsonify({'error': f'Disciplina debe ser una de: {", ".join(disciplinas_validas)}'}), 400
        vale.disciplina = data['disciplina']
    
    if 'satelite' in data:
        satelites_validos = ['#1', '#2', '#3']
        if data['satelite'] not in satelites_validos:
            return jsonify({'error': f'Satélite debe ser uno de: {", ".join(satelites_validos)}'}), 400
        vale.satelite = data['satelite']
    
    if 'cantidad_salida' in data:
        try:
            cantidad_salida = int(data['cantidad_salida'])
            if cantidad_salida < 0:
                return jsonify({'error': 'Cantidad debe ser positiva'}), 400
            vale.cantidad_salida = cantidad_salida
        except (ValueError, TypeError):
            return jsonify({'error': 'Cantidad debe ser un número entero'}), 400
    
    if 'stock_actual' in data:
        try:
            stock_actual = int(data['stock_actual'])
            if stock_actual < 0:
                return jsonify({'error': 'Stock debe ser positivo'}), 400
            vale.stock_actual = stock_actual
        except (ValueError, TypeError):
            return jsonify({'error': 'Stock debe ser un número entero'}), 400
    
    if 'observaciones' in data:
        vale.observaciones = data['observaciones']
    
    if 'producto_id' in data:
        producto = Producto.query.get(data['producto_id'])
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        vale.producto_id = data['producto_id']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Vale actualizado exitosamente',
        'vale': vale.to_dict()
    }), 200


@bp.route('/<int:vale_id>', methods=['DELETE'])
@jwt_required()
def delete_vale(vale_id):
    """Delete a vale"""
    user_id = get_jwt_identity()
    vale = Vale.query.get(vale_id)
    
    if not vale:
        return jsonify({'error': 'Vale no encontrado'}), 404
    
    # Check if user is owner or admin
    user = Usuario.query.get(user_id)
    if vale.usuario_id != user_id and user.rol != 'admin':
        return jsonify({'error': 'No tiene permisos para eliminar este vale'}), 403
    
    db.session.delete(vale)
    db.session.commit()
    
    return jsonify({'message': 'Vale eliminado exitosamente'}), 200
