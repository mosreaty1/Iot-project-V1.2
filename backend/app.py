"""
Flask Backend API for Vehicle Pass Registration System
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config_by_name
from backend.database import DynamoDBManager
from backend.validators import validate_registration_data

# Initialize Flask app
app = Flask(__name__)
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config_by_name[env])

# Enable CORS
CORS(app, origins=app.config['CORS_ORIGINS'])

# Initialize DynamoDB
db = DynamoDBManager(
    region=app.config['AWS_REGION'],
    table_name=app.config['DYNAMODB_TABLE_NAME'],
    aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/api/register', methods=['POST'])
def register_vehicle():
    """Register a new vehicle with passes"""
    try:
        data = request.get_json()

        # Validate input data
        is_valid, error_message = validate_registration_data(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400

        # Normalize plate number
        plate_number = data['plate_number'].upper().replace(' ', '')

        # Check if vehicle already exists
        existing = db.get_vehicle(plate_number)
        if existing:
            return jsonify({
                'error': 'Vehicle already registered',
                'plate_number': plate_number
            }), 409

        # Prepare vehicle data
        vehicle_data = {
            'plate_number': plate_number,
            'name': data['name'],
            'car_type': data['car_type'],
            'email': data['email'],
            'phone_number': data['phone_number'],
            'total_passes': int(data['passes']),
            'remaining_passes': int(data['passes']),
            'registered_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }

        # Save to DynamoDB
        db.create_vehicle(vehicle_data)

        return jsonify({
            'message': 'Vehicle registered successfully',
            'data': vehicle_data
        }), 201

    except Exception as e:
        app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/verify', methods=['POST'])
def verify_vehicle():
    """Verify vehicle and check remaining passes (called by Raspberry Pi)"""
    try:
        data = request.get_json()
        plate_number = data.get('plate_number', '').upper().replace(' ', '')

        if not plate_number:
            return jsonify({'error': 'Plate number is required'}), 400

        # Get vehicle from database
        vehicle = db.get_vehicle(plate_number)

        if not vehicle:
            return jsonify({
                'authorized': False,
                'message': 'Vehicle not registered'
            }), 200

        # Check if vehicle has remaining passes
        if vehicle.get('remaining_passes', 0) <= 0:
            return jsonify({
                'authorized': False,
                'message': 'No remaining passes',
                'name': vehicle.get('name'),
                'remaining_passes': 0
            }), 200

        # Vehicle authorized
        return jsonify({
            'authorized': True,
            'message': 'Access granted',
            'name': vehicle.get('name'),
            'remaining_passes': vehicle.get('remaining_passes'),
            'car_type': vehicle.get('car_type')
        }), 200

    except Exception as e:
        app.logger.error(f"Verification error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/deduct-pass', methods=['POST'])
def deduct_pass():
    """Deduct a pass after successful entry (called by Raspberry Pi)"""
    try:
        data = request.get_json()
        plate_number = data.get('plate_number', '').upper().replace(' ', '')

        if not plate_number:
            return jsonify({'error': 'Plate number is required'}), 400

        # Get vehicle from database
        vehicle = db.get_vehicle(plate_number)

        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404

        # Deduct pass
        success = db.deduct_pass(plate_number)

        if success:
            updated_vehicle = db.get_vehicle(plate_number)
            return jsonify({
                'message': 'Pass deducted successfully',
                'remaining_passes': updated_vehicle.get('remaining_passes')
            }), 200
        else:
            return jsonify({'error': 'Failed to deduct pass'}), 500

    except Exception as e:
        app.logger.error(f"Pass deduction error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/vehicle/<plate_number>', methods=['GET'])
def get_vehicle_info(plate_number):
    """Get vehicle information"""
    try:
        plate_number = plate_number.upper().replace(' ', '')
        vehicle = db.get_vehicle(plate_number)

        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404

        return jsonify({'data': vehicle}), 200

    except Exception as e:
        app.logger.error(f"Get vehicle error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/vehicles', methods=['GET'])
def list_vehicles():
    """List all registered vehicles"""
    try:
        vehicles = db.list_all_vehicles()
        return jsonify({
            'data': vehicles,
            'count': len(vehicles)
        }), 200

    except Exception as e:
        app.logger.error(f"List vehicles error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/add-passes', methods=['POST'])
def add_passes():
    """Add more passes to an existing vehicle"""
    try:
        data = request.get_json()
        plate_number = data.get('plate_number', '').upper().replace(' ', '')
        passes_to_add = int(data.get('passes', 0))

        if not plate_number or passes_to_add <= 0:
            return jsonify({'error': 'Invalid input'}), 400

        vehicle = db.get_vehicle(plate_number)
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404

        success = db.add_passes(plate_number, passes_to_add)

        if success:
            updated_vehicle = db.get_vehicle(plate_number)
            return jsonify({
                'message': 'Passes added successfully',
                'remaining_passes': updated_vehicle.get('remaining_passes')
            }), 200
        else:
            return jsonify({'error': 'Failed to add passes'}), 500

    except Exception as e:
        app.logger.error(f"Add passes error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create DynamoDB table if it doesn't exist
    db.create_table()

    # Run Flask app
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
