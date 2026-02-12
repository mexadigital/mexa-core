from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.usuario import Usuario

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    # Check if user already exists
    if Usuario.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'El usuario ya existe'}), 400
    
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El email ya está registrado'}), 400
    
    # Create new user
    user = Usuario(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        nombre_completo=data.get('nombre_completo'),
        rol=data.get('rol', 'usuario')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Usuario registrado exitosamente',
        'user': user.to_dict()
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    
    # Find user
    user = Usuario.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    if not user.activo:
        return jsonify({'error': 'Usuario inactivo'}), 401
    
    # Create access token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login exitoso',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    user_id = get_jwt_identity()
    user = Usuario.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify(user.to_dict()), 200


@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    user_id = get_jwt_identity()
    user = Usuario.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Contraseñas requeridas'}), 400
    
    if not user.check_password(data['old_password']):
        return jsonify({'error': 'Contraseña actual incorrecta'}), 401
    
    user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200
