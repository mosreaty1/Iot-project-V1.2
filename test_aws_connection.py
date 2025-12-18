#!/usr/bin/env python3
"""
AWS Connection Test Script
Tests connection to AWS DynamoDB and verifies configuration
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Get credentials from .env
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'VehiclePassRegistrations')

print("=" * 60)
print("AWS DynamoDB Connection Test")
print("=" * 60)
print()

# Check if .env file exists
if not os.path.exists('.env'):
    print("❌ ERROR: .env file not found!")
    print("   → Copy .env.example to .env")
    print("   → Fill in your AWS credentials")
    print()
    print("   Run: cp .env.example .env")
    sys.exit(1)

print("Configuration:")
print(f"  Region: {AWS_REGION}")
print(f"  Table Name: {TABLE_NAME}")

if AWS_ACCESS_KEY_ID:
    print(f"  Access Key ID: {AWS_ACCESS_KEY_ID[:10]}...{AWS_ACCESS_KEY_ID[-4:]}")
else:
    print("  Access Key ID: ❌ NOT SET")

if AWS_SECRET_ACCESS_KEY:
    print(f"  Secret Access Key: {'*' * 20}...{AWS_SECRET_ACCESS_KEY[-4:]}")
else:
    print("  Secret Access Key: ❌ NOT SET")

print()
print("-" * 60)
print("Testing Connection...")
print("-" * 60)
print()

# Check if credentials are set
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    print("❌ FAILED: AWS credentials not configured")
    print()
    print("To fix this:")
    print("1. Edit your .env file")
    print("2. Add your AWS_ACCESS_KEY_ID")
    print("3. Add your AWS_SECRET_ACCESS_KEY")
    print()
    print("Get credentials from:")
    print("https://console.aws.amazon.com/iam/home#/users")
    sys.exit(1)

try:
    # Create DynamoDB client
    print("📡 Connecting to AWS DynamoDB...")
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    # Get table
    table = dynamodb.Table(TABLE_NAME)

    # Try to get table info
    print(f"📋 Checking table '{TABLE_NAME}'...")
    table.load()

    print()
    print("=" * 60)
    print("✅ SUCCESS! Connected to AWS DynamoDB")
    print("=" * 60)
    print()
    print("Table Information:")
    print(f"  Name: {table.table_name}")
    print(f"  Status: {table.table_status}")
    print(f"  Item Count: {table.item_count}")
    print(f"  Created: {table.creation_date_time}")
    print(f"  ARN: {table.table_arn}")
    print()

    # Try to scan the table
    print("-" * 60)
    print("Fetching registered vehicles...")
    print("-" * 60)
    print()

    response = table.scan(Limit=10)
    items = response.get('Items', [])

    if items:
        print(f"Found {len(items)} vehicle(s) in database:")
        print()
        for idx, item in enumerate(items, 1):
            print(f"{idx}. Plate: {item.get('plate_number')}")
            print(f"   Name: {item.get('name')}")
            print(f"   Remaining Passes: {item.get('remaining_passes')}/{item.get('total_passes')}")
            print()
    else:
        print("No vehicles registered yet.")
        print()
        print("To register a vehicle:")
        print("1. Start the backend: python backend/app.py")
        print("2. Open browser: http://localhost:8080")
        print("3. Fill in the registration form")
        print()

    print("=" * 60)
    print("🎉 All tests passed! Your AWS setup is working correctly.")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Start backend: python backend/app.py")
    print("2. Open frontend: http://localhost:8080")
    print("3. Register vehicles and test the system")
    print()

except NoCredentialsError:
    print()
    print("=" * 60)
    print("❌ ERROR: Unable to locate credentials")
    print("=" * 60)
    print()
    print("Solutions:")
    print("1. Check that .env file exists in the project root")
    print("2. Verify AWS_ACCESS_KEY_ID is set in .env")
    print("3. Verify AWS_SECRET_ACCESS_KEY is set in .env")
    print()
    print("Example .env file:")
    print("  AWS_REGION=us-east-1")
    print("  AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE")
    print("  AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCY")
    print()
    sys.exit(1)

except ClientError as e:
    error_code = e.response['Error']['Code']
    print()
    print("=" * 60)
    print(f"❌ ERROR: {error_code}")
    print("=" * 60)
    print()

    if error_code == 'ResourceNotFoundException':
        print(f"Table '{TABLE_NAME}' does not exist in region {AWS_REGION}")
        print()
        print("Solutions:")
        print("1. Auto-create: Run the backend to create the table automatically")
        print("   python backend/app.py")
        print()
        print("2. Manual create: Use AWS CLI")
        print(f"   aws dynamodb create-table \\")
        print(f"       --table-name {TABLE_NAME} \\")
        print("       --attribute-definitions AttributeName=plate_number,AttributeType=S \\")
        print("       --key-schema AttributeName=plate_number,KeyType=HASH \\")
        print("       --billing-mode PAY_PER_REQUEST \\")
        print(f"       --region {AWS_REGION}")
        print()
        print("3. Create via AWS Console:")
        print(f"   https://console.aws.amazon.com/dynamodb/home?region={AWS_REGION}")

    elif error_code == 'UnrecognizedClientException':
        print("Invalid AWS credentials")
        print()
        print("Solutions:")
        print("1. Check your AWS_ACCESS_KEY_ID in .env")
        print("2. Check your AWS_SECRET_ACCESS_KEY in .env")
        print("3. Verify credentials are not expired")
        print("4. Regenerate access keys in IAM Console:")
        print("   https://console.aws.amazon.com/iam/home#/users")

    elif error_code == 'InvalidClientTokenId':
        print("The security token is invalid")
        print()
        print("Solutions:")
        print("1. Your Access Key ID is incorrect")
        print("2. Regenerate access keys:")
        print("   - Go to IAM Console → Users → your-user")
        print("   - Security credentials → Create access key")
        print("   - Update .env with new credentials")

    elif error_code == 'SignatureDoesNotMatch':
        print("The request signature does not match")
        print()
        print("Solutions:")
        print("1. Your Secret Access Key is incorrect")
        print("2. Check for extra spaces or newlines in .env")
        print("3. Regenerate access keys in IAM Console")

    elif error_code == 'AccessDeniedException':
        print("Your IAM user doesn't have permission to access DynamoDB")
        print()
        print("Solutions:")
        print("1. Go to IAM Console")
        print("2. Select your user")
        print("3. Add permissions → Attach policies")
        print("4. Select: AmazonDynamoDBFullAccess")

    else:
        print(f"Error Message: {e.response['Error']['Message']}")
        print()
        print("Check AWS documentation for this error code:")
        print(f"https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/")

    print()
    sys.exit(1)

except Exception as e:
    print()
    print("=" * 60)
    print("❌ ERROR: Unexpected error")
    print("=" * 60)
    print()
    print(f"Error: {str(e)}")
    print()
    print("Solutions:")
    print("1. Check your .env file configuration")
    print("2. Verify AWS region is correct")
    print("3. Check your internet connection")
    print("4. View full error above for details")
    print()
    sys.exit(1)
