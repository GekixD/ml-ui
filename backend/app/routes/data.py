from flask import Blueprint, jsonify
from ..services.data_service import DataService

data_bp = Blueprint('data', __name__)
data_service = DataService()

@data_bp.route('/api/datasets', methods=['GET'])
def list_datasets():
    return jsonify({
        'datasets': data_service.get_available_datasets()
    })

@data_bp.route('/api/datasets/<dataset_name>/columns', methods=['GET'])
def get_columns(dataset_name):
    try:
        columns = data_service.get_columns(dataset_name)
        return jsonify({
            'columns': columns
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 404 