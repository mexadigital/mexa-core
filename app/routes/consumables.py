from flask import Blueprint, request, jsonify
import logging
from app.utils.audit import log_audit

logger = logging.getLogger(__name__)

consumables_bp = Blueprint('consumables', __name__)

# In-memory storage for consumables (for demonstration purposes)
consumables = []

@consumables_bp.route('/consumables', methods=['GET'])
def get_consumables():
    logger.debug(
        'Consumables list retrieved',
        extra={'count': len(consumables)}
    )
    return jsonify(consumables), 200

@consumables_bp.route('/consumables/<int:consumable_id>', methods=['GET'])
def get_consumable(consumable_id):
    consumable = next((c for c in consumables if c['id'] == consumable_id), None)
    if consumable:
        logger.debug(
            'Consumable retrieved',
            extra={'consumable_id': consumable_id}
        )
    else:
        logger.warning(
            'Consumable not found',
            extra={'consumable_id': consumable_id}
        )
    return jsonify(consumable), 200 if consumable else 404

@consumables_bp.route('/consumables', methods=['POST'])
def create_consumable():
    new_consumable = request.json
    total_price = sum(item['price'] * item['quantity'] for item in new_consumable['items'])
    new_consumable['total_price'] = total_price
    new_consumable['id'] = len(consumables) + 1  # Simple ID assignment
    consumables.append(new_consumable)
    
    # Log the creation audit
    log_audit(
        action='create',
        resource_type='consumable',
        resource_id=new_consumable['id'],
        new_values=new_consumable
    )
    
    logger.info(
        'Consumable created',
        extra={'consumable_id': new_consumable['id'], 'total_price': total_price}
    )
    
    return jsonify(new_consumable), 201

@consumables_bp.route('/consumables/<int:consumable_id>', methods=['PUT'])
def update_consumable(consumable_id):
    consumable = next((c for c in consumables if c['id'] == consumable_id), None)
    if not consumable:
        logger.warning(
            'Consumable not found for update',
            extra={'consumable_id': consumable_id}
        )
        return jsonify({'message': 'Not found'}), 404
    
    old_data = consumable.copy()
    updated_data = request.json
    consumable.update(updated_data)
    consumable['total_price'] = sum(item['price'] * item['quantity'] for item in consumable.get('items', []))
    
    # Log the update audit
    log_audit(
        action='update',
        resource_type='consumable',
        resource_id=consumable_id,
        old_values=old_data,
        new_values=consumable
    )
    
    logger.info(
        'Consumable updated',
        extra={'consumable_id': consumable_id, 'old_data': old_data, 'new_data': consumable}
    )
    
    return jsonify(consumable), 200

@consumables_bp.route('/consumables/<int:consumable_id>', methods=['DELETE'])
def delete_consumable(consumable_id):
    global consumables
    consumable = next((c for c in consumables if c['id'] == consumable_id), None)
    
    if not consumable:
        logger.warning(
            'Consumable not found for deletion',
            extra={'consumable_id': consumable_id}
        )
        return jsonify({'message': 'Not found'}), 404
    
    # Store old data before deletion
    old_data = consumable.copy()
    consumables = [c for c in consumables if c['id'] != consumable_id]
    
    # Log the deletion audit
    log_audit(
        action='delete',
        resource_type='consumable',
        resource_id=consumable_id,
        old_values=old_data
    )
    
    logger.info(
        'Consumable deleted',
        extra={'consumable_id': consumable_id, 'old_data': old_data}
    )
    
    return jsonify({'message': 'Deleted successfully'}), 204
