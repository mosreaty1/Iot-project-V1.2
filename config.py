"""
Configuration file for Vehicle Pass Registration System
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

    # AWS Configuration
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    # DynamoDB Configuration
    DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'VehiclePassRegistrations')

    # S3 Configuration (for storing vehicle images)
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'vehicle-pass-images')

    # Raspberry Pi Configuration
    RPI_API_URL = os.getenv('RPI_API_URL', 'http://localhost:5000')

    # Pass Configuration
    MIN_PASSES = 5
    MAX_PASSES = 10

    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Add production-specific settings

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
