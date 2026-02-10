from flask import Blueprint, request, jsonify

epp_bp = Blueprint('epp', __name__)

# In-memory storage for example purposes
epp_resources = {}

# Create an EPP resource
@epp_bp.route('/epp', methods=['POST'])
def create_epp():
    data = request.json
    epp_id = len(epp_resources) + 1
    epp_resources[epp_id] = data
    return jsonify({'id': epp_id, 'data': data}), 201

# Read an EPP resource
@epp_bp.route('/epp/<int:epp_id>', methods=['GET'])
def read_epp(epp_id):
    epp = epp_resources.get(epp_id)
    if epp is None:
        return jsonify({'error': 'EPP not found'}), 404
    return jsonify({'id': epp_id, 'data': epp}), 200

# Update an EPP resource
@epp_bp.route('/epp/<int:epp_id>', methods=['PUT'])
def update_epp(epp_id):
    if epp_id not in epp_resources:
        return jsonify({'error': 'EPP not found'}), 404
    data = request.json
    epp_resources[epp_id] = data
    return jsonify({'id': epp_id, 'data': data}), 200

# Delete an EPP resource
@epp_bp.route('/epp/<int:epp_id>', methods=['DELETE'])
def delete_epp(epp_id):
    if epp_id not in epp_resources:
        return jsonify({'error': 'EPP not found'}), 404
    del epp_resources[epp_id]
    return jsonify({'message': 'EPP deleted'}), 204
