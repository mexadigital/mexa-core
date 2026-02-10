from flask import Blueprint, request, jsonify

consumables_bp = Blueprint('consumables', __name__)

# In-memory storage for consumables (for demonstration purposes)
consumables = []

@consumables_bp.route('/consumables', methods=['GET'])
def get_consumables():
    return jsonify(consumables), 200

@consumables_bp.route('/consumables/<int:consumable_id>', methods=['GET'])
def get_consumable(consumable_id):
    consumable = next((c for c in consumables if c['id'] == consumable_id), None)
    return jsonify(consumable), 200 if consumable else 404

@consumables_bp.route('/consumables', methods=['POST'])
def create_consumable():
    new_consumable = request.json
    total_price = sum(item['price'] * item['quantity'] for item in new_consumable['items'])
    new_consumable['total_price'] = total_price
    new_consumable['id'] = len(consumables) + 1  # Simple ID assignment
    consumables.append(new_consumable)
    return jsonify(new_consumable), 201

@consumables_bp.route('/consumables/<int:consumable_id>', methods=['PUT'])
def update_consumable(consumable_id):
    consumable = next((c for c in consumables if c['id'] == consumable_id), None)
    if not consumable:
        return jsonify({'message': 'Not found'}), 404
    updated_data = request.json
    consumable.update(updated_data)
    consumable['total_price'] = sum(item['price'] * item['quantity'] for item in consumable.get('items', []))
    return jsonify(consumable), 200

@consumables_bp.route('/consumables/<int:consumable_id>', methods=['DELETE'])
def delete_consumable(consumable_id):
    global consumables
    consumables = [c for c in consumables if c['id'] != consumable_id]
    return jsonify({'message': 'Deleted successfully'}), 204
