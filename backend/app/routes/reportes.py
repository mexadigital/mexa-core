from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

bp = Blueprint('reportes', __name__)


@bp.route('/diario', methods=['GET'])
@jwt_required()
def get_reporte_diario():
    """Generate daily report"""
    # TODO: Implement report generation
    # This will be implemented in Phase 2 with Celery
    return jsonify({'message': 'Reporte diario - En desarrollo'}), 200


@bp.route('/semanal', methods=['GET'])
@jwt_required()
def get_reporte_semanal():
    """Generate weekly report"""
    # TODO: Implement report generation
    # This will be implemented in Phase 2 with Celery
    return jsonify({'message': 'Reporte semanal - En desarrollo'}), 200
