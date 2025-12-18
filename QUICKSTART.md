# Quick Start Guide - AWS Connection

## 🚀 Get Up and Running in 10 Minutes

### Step 1: Get AWS Credentials (5 minutes)

#### A. Create AWS Account (if you don't have one)
1. Go to https://aws.amazon.com/free/
2. Click **"Create a Free Account"**
3. Follow the registration process
4. **Note:** You need a credit card, but won't be charged (Free Tier)

#### B. Get Access Keys
1. Sign in to AWS Console: https://console.aws.amazon.com/
2. Click your name (top right) → **Security credentials**
3. Scroll to **Access keys** section
4. Click **Create access key**
5. Select **"Application running outside AWS"**
6. Click **Next** → **Create access key**
7. **IMPORTANT:** Download the CSV file or copy the keys now!

You'll get:
```
Access key ID: AKIAIOSFODNN7EXAMPLE
Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

---

### Step 2: Configure Your Application (2 minutes)

```bash
# Navigate to project
cd /home/user/IOT-PROJECT-v2

# Create .env file
cp .env.example .env

# Edit .env file
nano .env
```

**Paste your credentials:**
```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE          # ← Paste your Access Key ID
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG...  # ← Paste your Secret Key

# Database
DYNAMODB_TABLE_NAME=VehiclePassRegistrations

# Flask
SECRET_KEY=change-this-to-random-string
DEBUG=True
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

---

### Step 3: Test AWS Connection (1 minute)

```bash
# Install dependencies
pip install -r requirements.txt

# Run connection test
python test_aws_connection.py
```

**Expected Output:**
```
============================================================
✅ SUCCESS! Connected to AWS DynamoDB
============================================================

Table Information:
  Name: VehiclePassRegistrations
  Status: ACTIVE
  Item Count: 0
  ...

🎉 All tests passed! Your AWS setup is working correctly.
```

**If you see errors:** See [Troubleshooting](#troubleshooting) below

---

### Step 4: Start the Backend (1 minute)

```bash
# Start Flask server
python backend/app.py
```

**Expected Output:**
```
 * Running on http://0.0.0.0:5000
 * DynamoDB table ready
```

---

### Step 5: Test Registration (1 minute)

Open another terminal:

```bash
# Test registration API
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "plate_number": "ABC-1234",
    "car_type": "Sedan",
    "email": "john@example.com",
    "phone_number": "+1234567890",
    "passes": 5
  }'
```

**Expected Response:**
```json
{
  "message": "Vehicle registered successfully",
  "data": {
    "plate_number": "ABC1234",
    "name": "John Doe",
    "remaining_passes": 5,
    ...
  }
}
```

---

### Step 6: View in AWS Console (Optional)

1. Go to https://console.aws.amazon.com/dynamodb/
2. Click **Tables** → **VehiclePassRegistrations**
3. Click **Explore table items**
4. You should see your registered vehicle!

---

## 🎉 Success!

Your database is now connected! Next steps:

1. **Open Frontend:** http://localhost:8080 (after running frontend server)
2. **Register vehicles** via the web form
3. **Setup Raspberry Pi** to complete the IoT system

---

## Troubleshooting

### ❌ "Unable to locate credentials"

**Problem:** .env file not found or empty

**Fix:**
```bash
# Make sure you're in the project root
cd /home/user/IOT-PROJECT-v2

# Check if .env exists
ls -la .env

# If not, create it
cp .env.example .env
nano .env  # Add your AWS credentials
```

---

### ❌ "The security token is invalid"

**Problem:** Wrong Access Key ID

**Fix:**
1. Go to AWS Console → IAM → Users → Security credentials
2. Create new access key
3. Update `.env` file with new keys

---

### ❌ "Table does not exist"

**Problem:** DynamoDB table not created

**Fix:**
```bash
# Run backend - it will auto-create the table
python backend/app.py
```

Or create manually:
```bash
aws dynamodb create-table \
    --table-name VehiclePassRegistrations \
    --attribute-definitions AttributeName=plate_number,AttributeType=S \
    --key-schema AttributeName=plate_number,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

---

### ❌ "Access Denied"

**Problem:** IAM user doesn't have DynamoDB permissions

**Fix:**
1. Go to AWS Console → IAM
2. Click **Users** → your username
3. Click **Add permissions**
4. Attach policy: **AmazonDynamoDBFullAccess**
5. Save

---

### ❌ Port 5000 already in use

**Problem:** Another application using port 5000

**Fix:**
```bash
# Option 1: Kill the process
sudo lsof -i :5000
sudo kill -9 <PID>

# Option 2: Change port in .env
PORT=5001
```

---

## Visual Guide: Where to Find AWS Credentials

### AWS Console → Security Credentials
```
┌─────────────────────────────────────┐
│  AWS Console                    👤 │
│                                     │
│  [Your Name] ▼                      │
│    - Account                        │
│    - Security credentials ← Click   │
│    - Billing                        │
└─────────────────────────────────────┘
```

### Access Keys Section
```
┌─────────────────────────────────────┐
│  Access keys                        │
│  ┌───────────────────────────────┐  │
│  │ ➕ Create access key          │  │
│  └───────────────────────────────┘  │
│                                     │
│  Active keys:                       │
│  • AKIA... (created 2 days ago)     │
└─────────────────────────────────────┘
```

---

## Complete .env Example

```env
# Flask Configuration
SECRET_KEY=your-super-secret-random-key-here-change-this
DEBUG=True
HOST=0.0.0.0
PORT=5000

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=VehiclePassRegistrations

# S3 Configuration (optional)
S3_BUCKET_NAME=vehicle-pass-images

# CORS Configuration
CORS_ORIGINS=*
```

---

## AWS Free Tier - Don't Worry About Costs

**DynamoDB Free Tier (Always Free):**
- ✅ 25 GB storage
- ✅ 25 read/write capacity units
- ✅ Enough for ~200 million requests/month

**Your usage:** Less than 1 MB, ~30,000 requests/month = **$0.00**

---

## Next Steps

✅ AWS Connected
✅ Backend Running
✅ Test Vehicle Registered

**Now do this:**

1. **Start Frontend:**
   ```bash
   cd frontend
   python3 -m http.server 8080
   ```
   Open: http://localhost:8080

2. **Setup Raspberry Pi:**
   Follow: `docs/SETUP_GUIDE.md`

3. **Wire Hardware:**
   Follow: `docs/WIRING_DIAGRAM.md`

---

## Need More Help?

- **Detailed AWS Setup:** `docs/AWS_SETUP.md`
- **Full Setup Guide:** `docs/SETUP_GUIDE.md`
- **API Documentation:** `docs/API.md`
- **AWS Documentation:** https://docs.aws.amazon.com/dynamodb/

---

## Quick Command Reference

```bash
# Test AWS connection
python test_aws_connection.py

# Start backend
python backend/app.py

# Start frontend
cd frontend && python3 -m http.server 8080

# View registered vehicles
curl http://localhost:5000/api/vehicles

# Check DynamoDB tables
aws dynamodb list-tables --region us-east-1

# View items in table
aws dynamodb scan --table-name VehiclePassRegistrations
```

---

**You're all set! 🚀**
