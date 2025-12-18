# AWS Setup Guide - Complete Walkthrough

This guide will walk you through setting up AWS DynamoDB for the Vehicle Pass Registration System.

## Table of Contents
1. [Create AWS Account](#1-create-aws-account)
2. [Create IAM User](#2-create-iam-user)
3. [Get Access Keys](#3-get-access-keys)
4. [Create DynamoDB Table](#4-create-dynamodb-table)
5. [Configure Application](#5-configure-application)
6. [Test Connection](#6-test-connection)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Create AWS Account

### If you don't have an AWS account:

1. Go to https://aws.amazon.com/
2. Click **"Create an AWS Account"**
3. Fill in your details:
   - Email address
   - Password
   - AWS account name
4. Choose **Personal** or **Business** account
5. Enter payment information (credit/debit card)
   - AWS Free Tier is available for 12 months
   - DynamoDB offers 25GB free storage permanently
6. Verify your identity (phone verification)
7. Choose **Basic Support - Free** plan
8. Wait for account activation (can take a few minutes)

### Sign In
1. Go to https://console.aws.amazon.com/
2. Sign in with your root account email and password

---

## 2. Create IAM User

**Important:** Don't use root account credentials. Create an IAM user instead.

### Step-by-Step:

1. **Open IAM Console**
   - In AWS Console, search for "IAM" in the top search bar
   - Click **IAM** (Identity and Access Management)

2. **Create New User**
   - Click **Users** in the left sidebar
   - Click **Add users** button
   - Enter username: `vehicle-pass-system`
   - Select **Access key - Programmatic access**
   - Click **Next: Permissions**

3. **Attach Policies**
   - Click **Attach existing policies directly**
   - Search and select these policies:
     - ✅ **AmazonDynamoDBFullAccess** (for database access)
     - ✅ **AmazonS3FullAccess** (optional, for storing images)
   - Click **Next: Tags**

4. **Add Tags (Optional)**
   - Key: `Project`, Value: `VehiclePassSystem`
   - Click **Next: Review**

5. **Review and Create**
   - Review your selections
   - Click **Create user**

---

## 3. Get Access Keys

### After creating the user:

1. **Download Credentials**
   - You'll see: "Success" with user details
   - **IMPORTANT:** This is the ONLY time you can see the secret key!
   - Click **Download .csv** button
   - Save the file securely

2. **Your credentials will look like this:**
   ```
   Access key ID: AKIAIOSFODNN7EXAMPLE
   Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   ```

3. **Keep these secure!**
   - Never commit to Git
   - Never share publicly
   - Store in password manager

---

## 4. Create DynamoDB Table

You have two options: **Automatic** (recommended) or **Manual**.

### Option A: Automatic Creation (Recommended)

The application will create the table automatically when you first run it.

Just configure your `.env` file (see step 5) and run the backend:
```bash
python backend/app.py
```

The table will be created automatically on first startup.

---

### Option B: Manual Creation

If you prefer to create the table manually:

#### Via AWS Console (Web Interface):

1. **Open DynamoDB Console**
   - Search for "DynamoDB" in AWS Console
   - Click **DynamoDB**

2. **Create Table**
   - Click **Create table** button

3. **Configure Table**
   - **Table name:** `VehiclePassRegistrations`
   - **Partition key:** `plate_number` (String)
   - Leave Sort key empty
   - **Table settings:** Default settings
   - **Read/write capacity:** On-demand (recommended)
   - Click **Create table**

4. **Wait for Creation**
   - Status will show "Creating..."
   - Wait until status is "Active" (30-60 seconds)

#### Via AWS CLI:

```bash
# Install AWS CLI first (if not installed)
# For Mac: brew install awscli
# For Ubuntu: sudo apt install awscli
# For Windows: Download from https://aws.amazon.com/cli/

# Configure AWS CLI
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Default region: us-east-1
# Default output format: json

# Create table
aws dynamodb create-table \
    --table-name VehiclePassRegistrations \
    --attribute-definitions AttributeName=plate_number,AttributeType=S \
    --key-schema AttributeName=plate_number,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1

# Verify table was created
aws dynamodb list-tables --region us-east-1
```

---

## 5. Configure Application

### Step 1: Create `.env` file

```bash
cd /home/user/IOT-PROJECT-v2

# Copy example file
cp .env.example .env

# Edit the file
nano .env  # or use your favorite editor
```

### Step 2: Fill in your AWS credentials

```env
# Flask Configuration
SECRET_KEY=your-random-secret-key-change-this-in-production
DEBUG=True
HOST=0.0.0.0
PORT=5000

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE          # ← YOUR ACCESS KEY HERE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG...  # ← YOUR SECRET KEY HERE

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=VehiclePassRegistrations

# S3 Configuration (optional)
S3_BUCKET_NAME=vehicle-pass-images

# CORS Configuration
CORS_ORIGINS=*
```

### Step 3: Generate a secret key

```bash
# Generate a random secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Copy the output and paste it as SECRET_KEY in .env
```

### Important Notes:
- Replace `AKIAIOSFODNN7EXAMPLE` with your actual Access Key ID
- Replace the secret access key with your actual secret key
- Change `SECRET_KEY` to a random string
- For production, set `DEBUG=False`

---

## 6. Test Connection

### Test 1: Verify AWS Credentials

```bash
# Test with AWS CLI
aws dynamodb list-tables --region us-east-1

# You should see:
# {
#     "TableNames": [
#         "VehiclePassRegistrations"
#     ]
# }
```

### Test 2: Test with Python

Create a test file `test_aws_connection.py`:

```python
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from .env
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'VehiclePassRegistrations')

print("Testing AWS Connection...")
print(f"Region: {AWS_REGION}")
print(f"Table: {TABLE_NAME}")
print(f"Access Key: {AWS_ACCESS_KEY_ID[:10]}..." if AWS_ACCESS_KEY_ID else "Access Key: NOT SET")
print()

try:
    # Create DynamoDB client
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    # Get table
    table = dynamodb.Table(TABLE_NAME)

    # Try to get table info
    table.load()

    print("✅ SUCCESS! Connected to DynamoDB")
    print(f"✅ Table '{TABLE_NAME}' exists")
    print(f"   - Table Status: {table.table_status}")
    print(f"   - Item Count: {table.item_count}")
    print(f"   - Table ARN: {table.table_arn}")

except ClientError as e:
    error_code = e.response['Error']['Code']

    if error_code == 'ResourceNotFoundException':
        print(f"❌ ERROR: Table '{TABLE_NAME}' does not exist")
        print("   → Run the backend to auto-create the table")
        print("   → Or create it manually in AWS Console")
    elif error_code == 'UnrecognizedClientException':
        print("❌ ERROR: Invalid AWS credentials")
        print("   → Check your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env")
    else:
        print(f"❌ ERROR: {error_code}")
        print(f"   Message: {e.response['Error']['Message']}")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print("   → Check your .env file configuration")
```

Run the test:
```bash
python test_aws_connection.py
```

**Expected Output (Success):**
```
Testing AWS Connection...
Region: us-east-1
Table: VehiclePassRegistrations
Access Key: AKIAIOSFO...

✅ SUCCESS! Connected to DynamoDB
✅ Table 'VehiclePassRegistrations' exists
   - Table Status: ACTIVE
   - Item Count: 0
   - Table ARN: arn:aws:dynamodb:us-east-1:123456789:table/VehiclePassRegistrations
```

### Test 3: Test Backend API

```bash
# Start the backend
python backend/app.py

# In another terminal, test the health endpoint
curl http://localhost:5000/health

# Expected output:
# {"status":"healthy","timestamp":"2025-01-15T10:30:00.000Z"}

# Test registration
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "plate_number": "TEST123",
    "car_type": "Sedan",
    "email": "test@example.com",
    "phone_number": "+1234567890",
    "passes": 5
  }'

# Expected output:
# {"message":"Vehicle registered successfully","data":{...}}
```

### Test 4: Verify Data in DynamoDB

```bash
# Check if data was stored
aws dynamodb scan --table-name VehiclePassRegistrations --region us-east-1

# Or use Python
python -c "
import boto3
from dotenv import load_dotenv
import os
load_dotenv()
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('VehiclePassRegistrations')
response = table.scan()
print('Items in database:', response['Items'])
"
```

---

## 7. Troubleshooting

### Problem 1: "Unable to locate credentials"

**Error Message:**
```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

**Solution:**
1. Check that `.env` file exists in project root
2. Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set in `.env`
3. Make sure you're running from the correct directory
4. Check for typos in variable names

```bash
# Verify .env file
cat .env | grep AWS

# Should show:
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=AKIA...
# AWS_SECRET_ACCESS_KEY=...
```

---

### Problem 2: "The security token included in the request is invalid"

**Error Message:**
```
InvalidClientTokenId: The security token included in the request is invalid
```

**Solution:**
1. Your Access Key ID is incorrect
2. Regenerate access keys:
   - Go to IAM Console → Users → vehicle-pass-system
   - Click **Security credentials** tab
   - Click **Create access key**
   - Download new credentials
   - Update `.env` file

---

### Problem 3: "User is not authorized to perform: dynamodb:CreateTable"

**Error Message:**
```
AccessDeniedException: User is not authorized to perform: dynamodb:CreateTable
```

**Solution:**
1. Go to IAM Console
2. Click your user (vehicle-pass-system)
3. Click **Add permissions** → **Attach existing policies directly**
4. Search and select **AmazonDynamoDBFullAccess**
5. Click **Add permissions**

---

### Problem 4: "Table does not exist"

**Error Message:**
```
ResourceNotFoundException: Requested resource not found: Table: VehiclePassRegistrations not found
```

**Solution:**
1. Create the table manually (see Option B above)
2. Or run the backend - it will auto-create the table:
   ```bash
   python backend/app.py
   ```

---

### Problem 5: "Region is not recognized"

**Error Message:**
```
Could not connect to the endpoint URL
```

**Solution:**
1. Check your AWS_REGION in `.env`
2. Common regions:
   - `us-east-1` (N. Virginia) - Default
   - `us-west-2` (Oregon)
   - `eu-west-1` (Ireland)
   - `ap-southeast-1` (Singapore)
3. Make sure region is lowercase

---

### Problem 6: Can't find `.env` file

```bash
# Make sure you're in the project root
cd /home/user/IOT-PROJECT-v2

# Check if .env exists
ls -la .env

# If not found, create it
cp .env.example .env
nano .env
```

---

## AWS Free Tier Limits

### DynamoDB Free Tier (Always Free):
- 25 GB of storage
- 25 read capacity units
- 25 write capacity units
- Enough for ~200 million requests/month

### Your Usage (Estimated):
- Small vehicle database: < 1 MB
- API calls: ~1000/day = ~30,000/month
- **Cost: $0** (well within free tier)

### Monitor Your Usage:
1. Go to AWS Console → Billing Dashboard
2. Click **Free Tier** in left sidebar
3. Check your DynamoDB usage

---

## Security Best Practices

### ✅ DO:
- Use IAM user (not root account)
- Store credentials in `.env` file
- Add `.env` to `.gitignore`
- Use least-privilege permissions
- Rotate access keys regularly
- Enable MFA on AWS account

### ❌ DON'T:
- Commit `.env` to Git
- Share credentials publicly
- Use root account for daily tasks
- Hard-code credentials in code
- Use overly permissive policies

---

## Quick Reference Commands

```bash
# Configure AWS CLI
aws configure

# List tables
aws dynamodb list-tables --region us-east-1

# Describe table
aws dynamodb describe-table --table-name VehiclePassRegistrations --region us-east-1

# Scan table (view all items)
aws dynamodb scan --table-name VehiclePassRegistrations --region us-east-1

# Get item count
aws dynamodb describe-table --table-name VehiclePassRegistrations \
  --query 'Table.ItemCount' --region us-east-1

# Delete table (careful!)
aws dynamodb delete-table --table-name VehiclePassRegistrations --region us-east-1
```

---

## Next Steps

After completing this setup:

1. ✅ AWS account created
2. ✅ IAM user with credentials
3. ✅ DynamoDB table created
4. ✅ `.env` configured
5. ✅ Connection tested

**You're ready to:**
- Start the backend server
- Test vehicle registration
- Deploy to production

See `docs/SETUP_GUIDE.md` for deployment instructions.

---

## Need Help?

- **AWS Documentation:** https://docs.aws.amazon.com/dynamodb/
- **AWS Free Tier:** https://aws.amazon.com/free/
- **IAM Best Practices:** https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **Boto3 Docs:** https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

---

## Summary Checklist

- [ ] Created AWS account
- [ ] Created IAM user with DynamoDB permissions
- [ ] Downloaded access keys
- [ ] Created DynamoDB table (or ready for auto-create)
- [ ] Created `.env` file with credentials
- [ ] Tested connection with Python script
- [ ] Backend server starts successfully
- [ ] Can register test vehicle
- [ ] Data appears in DynamoDB

**All checked?** You're ready to use the system! 🚀
