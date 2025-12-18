"""
DynamoDB Manager for Vehicle Pass Registration System
"""
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DynamoDBManager:
    """Manages DynamoDB operations for vehicle registration"""

    def __init__(self, region, table_name, aws_access_key_id=None, aws_secret_access_key=None):
        """Initialize DynamoDB connection"""
        self.table_name = table_name
        self.region = region

        # Initialize boto3 client
        if aws_access_key_id and aws_secret_access_key:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
        else:
            # Use IAM role or environment credentials
            self.dynamodb = boto3.resource('dynamodb', region_name=region)

        self.table = self.dynamodb.Table(table_name)

    def create_table(self):
        """Create DynamoDB table if it doesn't exist"""
        try:
            # Check if table exists
            self.table.load()
            logger.info(f"Table {self.table_name} already exists")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create table
                try:
                    table = self.dynamodb.create_table(
                        TableName=self.table_name,
                        KeySchema=[
                            {
                                'AttributeName': 'plate_number',
                                'KeyType': 'HASH'  # Partition key
                            }
                        ],
                        AttributeDefinitions=[
                            {
                                'AttributeName': 'plate_number',
                                'AttributeType': 'S'
                            }
                        ],
                        BillingMode='PAY_PER_REQUEST'  # On-demand pricing
                    )

                    # Wait for table to be created
                    table.meta.client.get_waiter('table_exists').wait(
                        TableName=self.table_name
                    )
                    logger.info(f"Table {self.table_name} created successfully")
                    return True
                except Exception as create_error:
                    logger.error(f"Error creating table: {str(create_error)}")
                    return False
            else:
                logger.error(f"Error checking table: {str(e)}")
                return False

    def create_vehicle(self, vehicle_data):
        """Create a new vehicle registration"""
        try:
            response = self.table.put_item(
                Item=vehicle_data,
                ConditionExpression='attribute_not_exists(plate_number)'
            )
            logger.info(f"Vehicle {vehicle_data['plate_number']} created successfully")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning(f"Vehicle {vehicle_data['plate_number']} already exists")
            else:
                logger.error(f"Error creating vehicle: {str(e)}")
            return False

    def get_vehicle(self, plate_number):
        """Get vehicle by plate number"""
        try:
            response = self.table.get_item(
                Key={'plate_number': plate_number}
            )
            return response.get('Item', None)
        except ClientError as e:
            logger.error(f"Error getting vehicle: {str(e)}")
            return None

    def deduct_pass(self, plate_number):
        """Deduct one pass from vehicle"""
        try:
            response = self.table.update_item(
                Key={'plate_number': plate_number},
                UpdateExpression='SET remaining_passes = remaining_passes - :decrement',
                ConditionExpression='remaining_passes > :zero',
                ExpressionAttributeValues={
                    ':decrement': 1,
                    ':zero': 0
                },
                ReturnValues='UPDATED_NEW'
            )
            logger.info(f"Pass deducted for vehicle {plate_number}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning(f"No remaining passes for vehicle {plate_number}")
            else:
                logger.error(f"Error deducting pass: {str(e)}")
            return False

    def add_passes(self, plate_number, passes_to_add):
        """Add passes to vehicle"""
        try:
            response = self.table.update_item(
                Key={'plate_number': plate_number},
                UpdateExpression='SET remaining_passes = remaining_passes + :increment, total_passes = total_passes + :increment',
                ExpressionAttributeValues={
                    ':increment': passes_to_add
                },
                ReturnValues='UPDATED_NEW'
            )
            logger.info(f"Added {passes_to_add} passes to vehicle {plate_number}")
            return True
        except ClientError as e:
            logger.error(f"Error adding passes: {str(e)}")
            return False

    def list_all_vehicles(self):
        """List all vehicles"""
        try:
            response = self.table.scan()
            vehicles = response.get('Items', [])

            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                vehicles.extend(response.get('Items', []))

            return vehicles
        except ClientError as e:
            logger.error(f"Error listing vehicles: {str(e)}")
            return []

    def update_vehicle_status(self, plate_number, status):
        """Update vehicle status (active, suspended, etc.)"""
        try:
            response = self.table.update_item(
                Key={'plate_number': plate_number},
                UpdateExpression='SET #status = :status',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': status
                },
                ReturnValues='UPDATED_NEW'
            )
            logger.info(f"Status updated for vehicle {plate_number}")
            return True
        except ClientError as e:
            logger.error(f"Error updating status: {str(e)}")
            return False

    def delete_vehicle(self, plate_number):
        """Delete a vehicle registration"""
        try:
            response = self.table.delete_item(
                Key={'plate_number': plate_number}
            )
            logger.info(f"Vehicle {plate_number} deleted successfully")
            return True
        except ClientError as e:
            logger.error(f"Error deleting vehicle: {str(e)}")
            return False
