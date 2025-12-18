# Windows Setup Guide

## The Problem You Encountered

The command `cp .env.example .env` doesn't work on Windows because `cp` is a Unix/Linux command.

## Solution: Windows Commands

### Option 1: Use Windows `copy` command
```cmd
copy .env.example .env
```

### Option 2: Use PowerShell
```powershell
Copy-Item .env.example .env
```

---

## Complete Windows Setup Steps

### Step 1: Navigate to Project
```cmd
cd E:\IOT-PROJECT-v2
```

### Step 2: Create .env file
```cmd
copy .env.example .env
```

### Step 3: Edit .env file

**Option A: Use Notepad**
```cmd
notepad .env
```

**Option B: Use any text editor**
- Right-click `.env` file → Open with → Notepad/VS Code/etc.

### Step 4: Add Your AWS Credentials

Replace these lines in the `.env` file:
```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE          # ← Paste YOUR Access Key
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG...  # ← Paste YOUR Secret Key
```

**Important:** Delete "EXAMPLE" values and paste YOUR actual AWS credentials!

### Step 5: Save the file
- Press `Ctrl+S` in Notepad
- Close Notepad

### Step 6: Install Python Dependencies
```cmd
pip install -r requirements.txt
```

### Step 7: Test AWS Connection
```cmd
python test_aws_connection.py
```

---

## Common Windows Command Equivalents

| Linux/Mac Command | Windows Command | What it does |
|-------------------|-----------------|--------------|
| `cp file1 file2` | `copy file1 file2` | Copy file |
| `mv file1 file2` | `move file1 file2` OR `ren file1 file2` | Move/rename file |
| `ls` | `dir` | List files |
| `cat file` | `type file` | View file contents |
| `rm file` | `del file` | Delete file |
| `nano file` | `notepad file` | Edit file |
| `pwd` | `cd` | Show current directory |
| `clear` | `cls` | Clear screen |

---

## Alternative: Use Git Bash on Windows

If you have Git installed on Windows, you can use **Git Bash** which supports Linux commands:

1. Right-click in your project folder
2. Select **"Git Bash Here"**
3. Now you can use Linux commands like `cp`, `ls`, `nano`, etc.

```bash
# In Git Bash, these work:
cp .env.example .env
nano .env
```

---

## Your Next Steps

1. **Run this command in Windows Command Prompt:**
   ```cmd
   copy .env.example .env
   ```

2. **Edit the .env file:**
   ```cmd
   notepad .env
   ```

3. **Add your AWS credentials** (from AWS Console)

4. **Test connection:**
   ```cmd
   python test_aws_connection.py
   ```

5. **Start backend:**
   ```cmd
   python backend/app.py
   ```

---

## Need AWS Credentials?

Follow the guide in `QUICKSTART.md` to get your AWS Access Key and Secret Key.

Or follow these quick steps:
1. Go to https://console.aws.amazon.com/
2. Click your name → **Security credentials**
3. Scroll to **Access keys**
4. Click **Create access key**
5. Copy the Access Key ID and Secret Access Key
6. Paste them in your `.env` file

---

## Troubleshooting

### "python is not recognized"
- Install Python from https://www.python.org/downloads/
- Make sure to check **"Add Python to PATH"** during installation

### "pip is not recognized"
```cmd
python -m pip install -r requirements.txt
```

### Can't find .env file
- Windows might hide file extensions
- In File Explorer: View → Show → File name extensions
- The file should be named `.env` not `.env.txt`

### File already exists
If `.env` already exists and you want to overwrite:
```cmd
copy /Y .env.example .env
```

---

**You're ready to go! 🚀**
