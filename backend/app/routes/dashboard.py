from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.vale import Vale
from app.models.producto import Producto
from sqlalchemy import func
from datetime import datetime, date, timedelta

bp = Blueprint('dashboard', __name__)


@bp.route('/consumo-hoy', methods=['GET'])
@jwt_required()
def get_consumo_hoy():
    """Get consumption for today by discipline"""
    hoy = date.today()
    
    # Query consumption by discipline for today
    consumo = db.session.query(
        Vale.disciplina,
        func.sum(Vale.cantidad_salida).label('total')
    ).filter(
        Vale.fecha == hoy
    ).group_by(
        Vale.disciplina
    ).all()
    
    # Format results
    result = {
        'Civil': 0,
        'Mecánica': 0,
        'Eléctrica': 0,
        'Total': 0
    }
    
    for disciplina, total in consumo:
        result[disciplina] = int(total) if total else 0
        result['Total'] += result[disciplina]
    
    return jsonify(result), 200


@bp.route('/stock-actual', methods=['GET'])
@jwt_required()
def get_stock_actual():
    """Get current stock for all products based on latest vale"""
    # Get latest vale for each product
    subquery = db.session.query(
        Vale.producto_id,
        func.max(Vale.created_at).label('max_created')
    ).group_by(Vale.producto_id).subquery()
    
    vales_recientes = db.session.query(Vale).join(
        subquery,
        db.and_(
            Vale.producto_id == subquery.c.producto_id,
            Vale.created_at == subquery.c.max_created
        )
    ).all()
    
    # Get all products
    productos = Producto.query.filter_by(activo=True).all()
    
    # Create stock dictionary
    stock_dict = {}
    for vale in vales_recientes:
        stock_dict[vale.producto_id] = vale.stock_actual
    
    # Build result with all products
    result = []
    for producto in productos:
        stock_actual = stock_dict.get(producto.id, 0)
        result.append({
            'producto_id': producto.id,
            'producto_nombre': producto.nombre,
            'stock_actual': stock_actual,
            'stock_minimo': producto.stock_minimo,
            'alerta': stock_actual < producto.stock_minimo
        })
    
    return jsonify(result), 200


@bp.route('/consumo-7-dias', methods=['GET'])
@jwt_required()
def get_consumo_7_dias():
    """Get consumption for last 7 days by discipline"""
    fecha_inicio = date.today() - timedelta(days=6)
    
    # Query consumption by discipline and date
    consumo = db.session.query(
        Vale.fecha,
        Vale.disciplina,
        func.sum(Vale.cantidad_salida).label('total')
    ).filter(
        Vale.fecha >= fecha_inicio
    ).group_by(
        Vale.fecha,
        Vale.disciplina
    ).order_by(
        Vale.fecha
    ).all()
    
    # Format results for charts
    result = {
        'dates': [],
        'Civil': [],
        'Mecánica': [],
        'Eléctrica': []
    }
    
    # Generate all dates for last 7 days
    all_dates = [(fecha_inicio + timedelta(days=i)) for i in range(7)]
    
    # Create consumption map
    consumo_map = {}
    for fecha, disciplina, total in consumo:
        key = f"{fecha}_{disciplina}"
        consumo_map[key] = int(total) if total else 0
    
    # Fill results
    for fecha in all_dates:
        result['dates'].append(fecha.isoformat())
        result['Civil'].append(consumo_map.get(f"{fecha}_Civil", 0))
        result['Mecánica'].append(consumo_map.get(f"{fecha}_Mecánica", 0))
        result['Eléctrica'].append(consumo_map.get(f"{fecha}_Eléctrica", 0))
    
    return jsonify(result), 200


@bp.route('/consumo-satelite-7-dias', methods=['GET'])
@jwt_required()
def get_consumo_satelite_7_dias():
    """Get consumption for last 7 days by satelite"""
    fecha_inicio = date.today() - timedelta(days=6)
    
    # Query consumption by satelite and date
    consumo = db.session.query(
        Vale.fecha,
        Vale.satelite,
        func.sum(Vale.cantidad_salida).label('total')
    ).filter(
        Vale.fecha >= fecha_inicio
    ).group_by(
        Vale.fecha,
        Vale.satelite
    ).order_by(
        Vale.fecha
    ).all()
    
    # Format results for charts
    result = {
        'dates': [],
        '#1': [],
        '#2': [],
        '#3': []
    }
    
    # Generate all dates for last 7 days
    all_dates = [(fecha_inicio + timedelta(days=i)) for i in range(7)]
    
    # Create consumption map
    consumo_map = {}
    for fecha, satelite, total in consumo:
        key = f"{fecha}_{satelite}"
        consumo_map[key] = int(total) if total else 0
    
    # Fill results
    for fecha in all_dates:
        result['dates'].append(fecha.isoformat())
        result['#1'].append(consumo_map.get(f"{fecha}_#1", 0))
        result['#2'].append(consumo_map.get(f"{fecha}_#2", 0))
        result['#3'].append(consumo_map.get(f"{fecha}_#3", 0))
    
    return jsonify(result), 200


@bp.route('/historico-30-dias', methods=['GET'])
@jwt_required()
def get_historico_30_dias():
    """Get historical records for last 30 days"""
    fecha_inicio = date.today() - timedelta(days=29)
    
    vales = Vale.query.filter(
        Vale.fecha >= fecha_inicio
    ).order_by(
        Vale.fecha.desc(),
        Vale.created_at.desc()
    ).all()
    
    return jsonify([vale.to_dict() for vale in vales]), 200


@bp.route('/resumen', methods=['GET'])
@jwt_required()
def get_resumen():
    """Get summary dashboard data"""
    return jsonify({
        'consumo_hoy': get_consumo_hoy()[0].json,
        'stock_actual': get_stock_actual()[0].json,
        'consumo_7_dias': get_consumo_7_dias()[0].json,
        'consumo_satelite_7_dias': get_consumo_satelite_7_dias()[0].json
    }), 200
