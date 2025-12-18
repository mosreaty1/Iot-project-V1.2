# Complete Windows Installation Guide

## 🪟 Vehicle Pass Registration System - Windows Setup

This guide provides complete step-by-step instructions for installing and running the Vehicle Pass Registration System on Windows.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Install Python](#install-python)
3. [Install Git](#install-git)
4. [Clone the Project](#clone-the-project)
5. [Setup AWS Account](#setup-aws-account)
6. [Configure the Application](#configure-the-application)
7. [Install Dependencies](#install-dependencies)
8. [Test AWS Connection](#test-aws-connection)
9. [Run the Backend](#run-the-backend)
10. [Run the Frontend](#run-the-frontend)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, you need:
- **Windows 10 or 11**
- **Internet connection**
- **AWS Account** (free tier available)
- **Administrator access** (for installing software)

---

## Install Python

### Step 1: Download Python

1. Go to https://www.python.org/downloads/
2. Click **"Download Python 3.11.x"** (or latest version)
3. Save the installer file

### Step 2: Install Python

1. **Run the installer**
2. ⚠️ **IMPORTANT:** Check **"Add Python to PATH"** (at bottom of installer)
3. Click **"Install Now"**
4. Wait for installation to complete
5. Click **"Close"**

### Step 3: Verify Installation

Open **Command Prompt** (press `Win + R`, type `cmd`, press Enter):

```cmd
python --version
```

You should see something like: `Python 3.11.x`

```cmd
pip --version
```

You should see: `pip 23.x.x from ...`

---

## Install Git

### Step 1: Download Git

1. Go to https://git-scm.com/download/win
2. Download the installer (64-bit or 32-bit based on your Windows)

### Step 2: Install Git

1. Run the installer
2. Use default settings (just keep clicking "Next")
3. Click "Install"
4. Click "Finish"

### Step 3: Verify Installation

Open Command Prompt:

```cmd
git --version
```

You should see: `git version 2.x.x`

---

## Clone the Project

### Step 1: Choose Installation Location

Decide where to install (e.g., `E:\Projects\`)

### Step 2: Open Command Prompt in That Location

**Method 1:** Using File Explorer
1. Open File Explorer
2. Navigate to your desired folder (e.g., `E:\Projects\`)
3. Click in the address bar, type `cmd`, press Enter

**Method 2:** Using cd command
```cmd
cd E:\Projects
```

### Step 3: Clone Repository

```cmd
git clone <repository-url>
cd IOT-PROJECT-v2
```

**Or if you downloaded as ZIP:**
1. Extract the ZIP file
2. Open Command Prompt in the extracted folder

---

## Setup AWS Account

### Step 1: Create AWS Account

1. Go to https://aws.amazon.com/
2. Click **"Create an AWS Account"**
3. Fill in:
   - Email address
   - Password
   - Account name
4. Enter credit card info (won't be charged with Free Tier)
5. Complete phone verification
6. Choose **"Basic Support - Free"**

### Step 2: Get AWS Credentials

1. Sign in to AWS Console: https://console.aws.amazon.com/
2. Click your name (top right) → **"Security credentials"**
3. Scroll to **"Access keys"** section
4. Click **"Create access key"**
5. Select **"Application running outside AWS"**
6. Click **Next** → **Create access key**
7. **IMPORTANT:** Download the CSV or copy both keys:
   - Access key ID: `AKIA...`
   - Secret access key: `wJalr...`
8. **Save these securely!** You won't see the secret key again

### Step 3: Create IAM Permissions (if needed)

1. Go to IAM Console: https://console.aws.amazon.com/iam/
2. Click **Users** → select your user
3. Click **Add permissions** → **Attach existing policies**
4. Select:
   - ✅ **AmazonDynamoDBFullAccess**
5. Click **Add permissions**

---

## Configure the Application

### Step 1: Create .env File

Open Command Prompt in project folder:

```cmd
cd E:\IOT-PROJECT-v2

REM Copy the example file
copy .env.example .env
```

### Step 2: Edit .env File

```cmd
notepad .env
```

This will open Notepad. Update these lines:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-random-key-change-this
DEBUG=True
HOST=0.0.0.0
PORT=5000

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...                    ← Paste YOUR Access Key ID here
AWS_SECRET_ACCESS_KEY=wJalr...               ← Paste YOUR Secret Key here

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=VehiclePassRegistrations

# S3 Configuration (optional)
S3_BUCKET_NAME=vehicle-pass-images

# CORS Configuration
CORS_ORIGINS=*
```

### Step 3: Generate Secret Key

Open PowerShell:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as `SECRET_KEY` in your `.env` file.

### Step 4: Save and Close

Press `Ctrl+S` to save, then close Notepad.

---

## Install Dependencies

### Step 1: Create Virtual Environment (Recommended)

```cmd
cd E:\IOT-PROJECT-v2

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
venv\Scripts\activate.bat
```

You should see `(venv)` at the beginning of your prompt.

### Step 2: Install Requirements

```cmd
pip install -r requirements.txt
```

This will install all necessary Python packages (Flask, boto3, etc.)

**Note:** This may take 2-5 minutes depending on your internet speed.

---

## Test AWS Connection

Run the connection test script:

```cmd
python test_aws_connection.py
```

### Expected Output:

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

### If You See Errors:

See the [Troubleshooting](#troubleshooting) section below.

---

## Run the Backend

### Method 1: Using Batch File (Recommended)

```cmd
run_backend.bat
```

This will:
- Create virtual environment (if not exists)
- Install dependencies
- Check for .env file
- Start the Flask backend

### Method 2: Manual Start

```cmd
REM Make sure virtual environment is activated
venv\Scripts\activate.bat

REM Run backend
python backend\app.py
```

### Expected Output:

```
 * Running on http://0.0.0.0:5000
 * DynamoDB table 'VehiclePassRegistrations' is ready
 * Debug mode: on
```

**Keep this Command Prompt window open!** The backend is now running.

---

## Run the Frontend

### Step 1: Open New Command Prompt

Open a **new** Command Prompt window (don't close the backend window!)

### Step 2: Navigate to Frontend Folder

```cmd
cd E:\IOT-PROJECT-v2\frontend
```

### Step 3: Start HTTP Server

```cmd
python -m http.server 8080
```

### Step 4: Open Browser

Open your web browser and go to:

```
http://localhost:8080
```

You should see the Vehicle Registration form!

---

## Register Your First Vehicle

### Using the Web Form:

1. Open http://localhost:8080
2. Fill in:
   - **Name:** John Doe
   - **Plate Number:** ABC1234
   - **Car Type:** Sedan
   - **Email:** john@example.com
   - **Phone:** +1234567890
   - **Passes:** 5
3. Click **"Register Vehicle"**
4. You should see: "Vehicle registered successfully!"

### Verify in Admin Dashboard:

1. Open http://localhost:8080/admin.html
2. You should see ABC1234 listed with 5 passes

---

## Troubleshooting

### ❌ 'python' is not recognized

**Problem:** Python not installed or not in PATH

**Solution:**
1. Install Python from https://www.python.org/downloads/
2. **Important:** Check "Add Python to PATH" during installation
3. Restart Command Prompt
4. Try again

---

### ❌ 'pip' is not recognized

**Problem:** pip not in PATH

**Solution:**
```cmd
python -m pip install -r requirements.txt
```

---

### ❌ 'cp' is not recognized

**Problem:** Using Linux commands on Windows

**Solution:** Use Windows commands:
- `cp` → `copy`
- `ls` → `dir`
- `cat` → `type`
- `rm` → `del`

See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for full command reference.

---

### ❌ Unable to locate credentials

**Problem:** .env file missing or AWS credentials not set

**Solution:**
1. Check .env file exists:
   ```cmd
   dir .env
   ```
2. If not, create it:
   ```cmd
   copy .env.example .env
   notepad .env
   ```
3. Add your AWS credentials
4. Save and try again

---

### ❌ Access Denied / Invalid credentials

**Problem:** Wrong AWS credentials

**Solution:**
1. Go to AWS Console → IAM → Users → Security credentials
2. Create new access key
3. Update .env file with new keys
4. Make sure no extra spaces or quotes

---

### ❌ Table does not exist

**Problem:** DynamoDB table not created

**Solution:**
The backend creates the table automatically on first run:
```cmd
python backend\app.py
```

Wait for message: "DynamoDB table 'VehiclePassRegistrations' is ready"

---

### ❌ Port 5000 already in use

**Problem:** Another application using port 5000

**Solution 1:** Find and kill the process
```cmd
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Solution 2:** Change port in .env
```env
PORT=5001
```

---

### ❌ Cannot activate virtual environment

**Problem:** PowerShell execution policy

**Solution:**
If using PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

Or use Command Prompt instead:
```cmd
venv\Scripts\activate.bat
```

---

### ❌ ModuleNotFoundError

**Problem:** Dependencies not installed

**Solution:**
```cmd
REM Activate virtual environment
venv\Scripts\activate.bat

REM Reinstall dependencies
pip install -r requirements.txt
```

---

## Windows Command Reference

| Linux/Mac Command | Windows Command | Description |
|-------------------|-----------------|-------------|
| `cp file1 file2` | `copy file1 file2` | Copy file |
| `mv file1 file2` | `move file1 file2` | Move file |
| `ls` | `dir` | List files |
| `ls -la` | `dir /a` | List all files with details |
| `cat file` | `type file` | View file contents |
| `rm file` | `del file` | Delete file |
| `nano file` | `notepad file` | Edit file |
| `pwd` | `cd` | Show current directory |
| `clear` | `cls` | Clear screen |
| `chmod +x` | (not needed) | Make executable |
| `./script.sh` | `script.bat` | Run script |

---

## Quick Start Summary

For experienced users, here's the quick version:

```cmd
REM 1. Install Python (add to PATH!)
REM 2. Clone project
git clone <repo-url>
cd IOT-PROJECT-v2

REM 3. Configure AWS
copy .env.example .env
notepad .env
REM Add AWS credentials

REM 4. Install dependencies
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt

REM 5. Test connection
python test_aws_connection.py

REM 6. Run backend (keep window open)
run_backend.bat

REM 7. Run frontend (new window)
cd frontend
python -m http.server 8080

REM 8. Open browser
start http://localhost:8080
```

---

## Additional Resources

- **Main README:** [README.md](README.md)
- **Quick Start Guide:** [QUICKSTART.md](QUICKSTART.md)
- **AWS Setup:** [docs/AWS_SETUP.md](docs/AWS_SETUP.md)
- **Windows Commands:** [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
- **Full Setup Guide:** [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)

---

## Getting Help

### Common Issues:
1. Check [Troubleshooting](#troubleshooting) section above
2. Read error messages carefully
3. Google the specific error message

### AWS Issues:
- AWS Documentation: https://docs.aws.amazon.com/dynamodb/
- AWS Support Forums: https://forums.aws.amazon.com/

### Python Issues:
- Python Documentation: https://docs.python.org/3/
- Stack Overflow: https://stackoverflow.com/questions/tagged/python

---

## Success Checklist

- [ ] Python installed and working (`python --version`)
- [ ] Git installed (`git --version`)
- [ ] Project cloned/downloaded
- [ ] AWS account created
- [ ] AWS credentials obtained
- [ ] .env file created with credentials
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] AWS connection test passed
- [ ] Backend running on port 5000
- [ ] Frontend accessible at http://localhost:8080
- [ ] Successfully registered test vehicle

---

## Next Steps

Once everything is working:

1. **Register vehicles** via the web interface
2. **View admin dashboard** at http://localhost:8080/admin.html
3. **Test the API** using the examples in [docs/API.md](docs/API.md)
4. **Setup Raspberry Pi** (if you have hardware) - see [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
5. **Deploy to production** - consider using cloud hosting

---

## Notes for Windows Users

### Virtual Environment Activation:
- **Command Prompt:** `venv\Scripts\activate.bat`
- **PowerShell:** `venv\Scripts\Activate.ps1`
- **Git Bash:** `source venv/Scripts/activate`

### Path Separators:
- Windows uses backslash `\` in paths
- Example: `python backend\app.py` (not `backend/app.py`)

### Text Editors:
- Notepad (built-in)
- VS Code (recommended): https://code.visualstudio.com/
- Notepad++: https://notepad-plus-plus.org/

### Alternative Terminals:
- **Command Prompt** (default)
- **PowerShell** (more powerful)
- **Git Bash** (Linux-like, comes with Git)
- **Windows Terminal** (modern, recommended): https://aka.ms/terminal

---

## Production Deployment on Windows

For production use on Windows:

### Option 1: Use Windows Server
- Install IIS (Internet Information Services)
- Use wfastcgi to host Flask app
- Configure SSL certificates

### Option 2: Use Cloud Services (Recommended)
- AWS EC2 (Linux instance)
- Azure App Service
- Google Cloud Run
- Heroku

See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for production deployment guide.

---

**🎉 Congratulations! You've successfully set up the Vehicle Pass Registration System on Windows!**

For questions or issues, check the documentation or create an issue on GitHub.
