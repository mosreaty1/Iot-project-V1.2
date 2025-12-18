"""
Input validation for Vehicle Pass Registration System
"""
import re


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number format"""
    # Remove spaces and special characters
    cleaned = re.sub(r'[^\d+]', '', phone)
    # Check if it's a valid international format
    return len(cleaned) >= 10


def validate_plate_number(plate_number):
    """Validate plate number format"""
    # Remove spaces and check if it has valid characters
    cleaned = plate_number.replace(' ', '').replace('-', '')
    # Should contain letters and numbers
    return len(cleaned) >= 3 and any(c.isalpha() for c in cleaned) and any(c.isdigit() for c in cleaned)


def validate_registration_data(data):
    """Validate complete registration data"""
    required_fields = ['name', 'plate_number', 'car_type', 'email', 'phone_number', 'passes']

    # Check required fields
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"

    # Validate name
    if len(data['name']) < 2:
        return False, "Name must be at least 2 characters"

    # Validate plate number
    if not validate_plate_number(data['plate_number']):
        return False, "Invalid plate number format"

    # Validate car type
    valid_car_types = ['Sedan', 'SUV', 'Hatchback', 'Truck', 'Electric']
    if data['car_type'] not in valid_car_types:
        return False, f"Invalid car type. Must be one of: {', '.join(valid_car_types)}"

    # Validate email
    if not validate_email(data['email']):
        return False, "Invalid email format"

    # Validate phone number
    if not validate_phone(data['phone_number']):
        return False, "Invalid phone number format"

    # Validate passes
    try:
        passes = int(data['passes'])
        if passes < 5 or passes > 10:
            return False, "Number of passes must be between 5 and 10"
    except (ValueError, TypeError):
        return False, "Invalid number of passes"

    return True, None
