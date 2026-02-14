from flask import Blueprint, request, jsonify
import logging
from app.utils.audit import log_audit

logger = logging.getLogger(__name__)

epp_bp = Blueprint('epp', __name__)

# In-memory storage for example purposes
epp_resources = {}

# Create an EPP resource
@epp_bp.route('/epp', methods=['POST'])
def create_epp():
    data = request.json
    epp_id = len(epp_resources) + 1
    epp_resources[epp_id] = data
    
    # Log the creation audit
    log_audit(
        action='create',
        resource_type='epp',
        resource_id=epp_id,
        new_values=data
    )
    
    logger.info(
        'EPP resource created',
        extra={'epp_id': epp_id, 'data': data}
    )
    
    return jsonify({'id': epp_id, 'data': data}), 201

# Read an EPP resource
@epp_bp.route('/epp/<int:epp_id>', methods=['GET'])
def read_epp(epp_id):
    epp = epp_resources.get(epp_id)
    if epp is None:
        logger.warning(
            'EPP resource not found',
            extra={'epp_id': epp_id}
        )
        return jsonify({'error': 'EPP not found'}), 404
    
    logger.debug(
        'EPP resource retrieved',
        extra={'epp_id': epp_id}
    )
    return jsonify({'id': epp_id, 'data': epp}), 200

# Update an EPP resource
@epp_bp.route('/epp/<int:epp_id>', methods=['PUT'])
def update_epp(epp_id):
    if epp_id not in epp_resources:
        logger.warning(
            'EPP resource not found for update',
            extra={'epp_id': epp_id}
        )
        return jsonify({'error': 'EPP not found'}), 404
    
    old_data = epp_resources[epp_id].copy()
    data = request.json
    epp_resources[epp_id] = data
    
    # Log the update audit
    log_audit(
        action='update',
        resource_type='epp',
        resource_id=epp_id,
        old_values=old_data,
        new_values=data
    )
    
    logger.info(
        'EPP resource updated',
        extra={'epp_id': epp_id, 'old_data': old_data, 'new_data': data}
    )
    
    return jsonify({'id': epp_id, 'data': data}), 200

# Delete an EPP resource
@epp_bp.route('/epp/<int:epp_id>', methods=['DELETE'])
def delete_epp(epp_id):
    if epp_id not in epp_resources:
        logger.warning(
            'EPP resource not found for deletion',
            extra={'epp_id': epp_id}
        )
        return jsonify({'error': 'EPP not found'}), 404
    
    old_data = epp_resources[epp_id].copy()
    del epp_resources[epp_id]
    
    # Log the deletion audit
    log_audit(
        action='delete',
        resource_type='epp',
        resource_id=epp_id,
        old_values=old_data
    )
    
    logger.info(
        'EPP resource deleted',
        extra={'epp_id': epp_id, 'old_data': old_data}
    )
    
    return jsonify({'message': 'EPP deleted'}), 204
