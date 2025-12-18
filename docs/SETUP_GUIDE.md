# Complete Setup Guide

## Step-by-Step Installation

### Prerequisites

Before starting, ensure you have:
- AWS Account with billing enabled
- Raspberry Pi 4 with Raspbian OS installed
- All hardware components (see README.md)
- Basic knowledge of Linux/Python

---

## Part 1: AWS Setup

### 1.1 Create IAM User

```bash
# Login to AWS Console
# Navigate to IAM -> Users -> Add User

# User details:
Username: vehicle-pass-system
Access type: Programmatic access

# Permissions:
Attach existing policies:
- AmazonDynamoDBFullAccess
- AmazonS3FullAccess (optional, for images)

# Save credentials:
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

### 1.2 Create DynamoDB Table

**Option A: Auto-create (Recommended)**
The application will create the table automatically on first run.

**Option B: Manual Creation**
```bash
aws dynamodb create-table \
    --table-name VehiclePassRegistrations \
    --attribute-definitions AttributeName=plate_number,AttributeType=S \
    --key-schema AttributeName=plate_number,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

### 1.3 Optional: Create S3 Bucket for Images
```bash
aws s3 mb s3://vehicle-pass-images --region us-east-1
```

---

## Part 2: Backend Server Setup

### 2.1 Server Preparation

You can use:
- AWS EC2 instance
- Digital Ocean Droplet
- Local server
- Raspberry Pi (separate from controller)

**Recommended: AWS EC2 t2.micro (Free Tier)**

```bash
# Launch EC2 instance
# - AMI: Ubuntu 22.04
# - Instance type: t2.micro
# - Security group: Allow ports 22, 5000, 8080

# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2.2 Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3-pip python3-venv -y

# Install Git
sudo apt install git -y

# Clone repository
git clone <your-repo-url>
cd IOT-PROJECT-v2
```

### 2.3 Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2.4 Configure Environment

```bash
# Create .env file
cp .env.example .env
nano .env
```

Edit with your AWS credentials:
```env
SECRET_KEY=your-random-secret-key-here
DEBUG=False
HOST=0.0.0.0
PORT=5000

AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

DYNAMODB_TABLE_NAME=VehiclePassRegistrations
```

### 2.5 Test Backend

```bash
# Run development server
python backend/app.py

# Test health endpoint
curl http://localhost:5000/health
```

### 2.6 Production Deployment

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app

# Create systemd service
sudo nano /etc/systemd/system/vehicle-pass.service
```

Service file content:
```ini
[Unit]
Description=Vehicle Pass Registration API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/IOT-PROJECT-v2
Environment="PATH=/home/ubuntu/IOT-PROJECT-v2/venv/bin"
ExecStart=/home/ubuntu/IOT-PROJECT-v2/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable vehicle-pass
sudo systemctl start vehicle-pass
sudo systemctl status vehicle-pass
```

---

## Part 3: Frontend Setup

### 3.1 Update API URLs

```bash
cd frontend

# Edit index.html
nano index.html
# Change: const API_URL = 'http://YOUR_BACKEND_IP:5000/api';

# Edit admin.html
nano admin.html
# Change: const API_URL = 'http://YOUR_BACKEND_IP:5000/api';
```

### 3.2 Serve Frontend

**Option A: Simple Python Server**
```bash
cd frontend
python3 -m http.server 8080
```

**Option B: Nginx (Production)**
```bash
sudo apt install nginx -y

# Create site configuration
sudo nano /etc/nginx/sites-available/vehicle-pass
```

Configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /home/ubuntu/IOT-PROJECT-v2/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/vehicle-pass /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Part 4: Raspberry Pi Setup

### 4.1 Initial Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Enable camera and I2C
sudo raspi-config
# Interface Options -> Camera -> Enable
# Interface Options -> I2C -> Enable
# Reboot

# Install system dependencies
sudo apt install -y \
    python3-pip \
    python3-opencv \
    tesseract-ocr \
    libtesseract-dev \
    libatlas-base-dev \
    git
```

### 4.2 Clone and Install

```bash
# Clone repository
cd ~
git clone <your-repo-url>
cd IOT-PROJECT-v2/raspberry_pi

# Install Python packages
pip3 install -r requirements.txt
```

### 4.3 Hardware Wiring

Follow the wiring diagram:

**Ultrasonic Sensor (HC-SR04)**
- VCC -> 5V
- GND -> GND
- TRIG -> GPIO 23
- ECHO -> GPIO 24 (with voltage divider: 1kΩ + 2kΩ)

**LCD Display (16x2)**
- VSS -> GND
- VDD -> 5V
- V0 -> Potentiometer (contrast)
- RS -> GPIO 7
- RW -> GND
- E -> GPIO 8
- D4 -> GPIO 25
- D5 -> GPIO 24
- D6 -> GPIO 23
- D7 -> GPIO 18
- A -> 5V (with 220Ω resistor)
- K -> GND

**LEDs (Traffic Light)**
- Red LED -> GPIO 17 (with 220Ω resistor) -> GND
- Green LED -> GPIO 27 (with 220Ω resistor) -> GND

**Servo Motor (Barrier)**
- Red (VCC) -> 5V
- Brown (GND) -> GND
- Orange (Signal) -> GPIO 22

**Camera**
- Connect to CSI port (ribbon cable)

### 4.4 Configure Settings

```bash
cd ~/IOT-PROJECT-v2/raspberry_pi
nano config/settings.py
```

Update API_URL:
```python
'API_URL': 'http://YOUR_BACKEND_SERVER_IP:5000',
```

### 4.5 Test Individual Components

```bash
# Test camera
libcamera-still -o test.jpg

# Test ultrasonic sensor
python3 -c "from modules.ultrasonic import UltrasonicSensor; s = UltrasonicSensor(); print(s.get_distance())"

# Test LCD
python3 -c "from modules.lcd_display import LCDDisplay; lcd = LCDDisplay(); lcd.display_message('Test', 'Working')"

# Test traffic light
python3 -c "from modules.traffic_light import TrafficLight; t = TrafficLight(); t.green(); import time; time.sleep(2); t.red()"

# Test barrier
python3 -c "from modules.barrier import BarrierControl; b = BarrierControl(); b.open(); import time; time.sleep(2); b.close()"
```

### 4.6 Run Main Controller

```bash
# Test run
python3 main.py

# Run in background with screen
sudo apt install screen -y
screen -S vehicle-pass
python3 main.py
# Press Ctrl+A, then D to detach
```

### 4.7 Auto-start on Boot

```bash
# Create systemd service
sudo nano /etc/systemd/system/vehicle-controller.service
```

Service content:
```ini
[Unit]
Description=Vehicle Access Controller
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/IOT-PROJECT-v2/raspberry_pi
ExecStart=/usr/bin/python3 /home/pi/IOT-PROJECT-v2/raspberry_pi/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable vehicle-controller
sudo systemctl start vehicle-controller
sudo systemctl status vehicle-controller
```

---

## Part 5: Testing End-to-End

### 5.1 Register a Test Vehicle

```bash
# Open browser
http://YOUR_BACKEND_IP:8080

# Fill form:
Name: Test User
Plate: TEST123
Car Type: Sedan
Email: test@example.com
Phone: +1234567890
Passes: 5

# Submit
```

### 5.2 Verify in Admin Dashboard

```bash
# Open admin panel
http://YOUR_BACKEND_IP:8080/admin.html

# You should see TEST123 with 5 remaining passes
```

### 5.3 Test Access Control

1. Approach ultrasonic sensor (within 50cm)
2. System should:
   - Capture image
   - Recognize plate (or use mock mode)
   - Display welcome message
   - Open barrier
   - Deduct pass

### 5.4 Verify Pass Deduction

Check admin dashboard - passes should decrease from 5 to 4.

---

## Part 6: Troubleshooting

### Backend Issues

**Problem: Can't connect to DynamoDB**
```bash
# Test AWS credentials
aws dynamodb list-tables --region us-east-1

# Check .env file
cat .env

# View logs
journalctl -u vehicle-pass -f
```

**Problem: Port 5000 already in use**
```bash
# Find process
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>

# Or change port in .env
```

### Raspberry Pi Issues

**Problem: Camera not working**
```bash
# Check if enabled
vcgencmd get_camera

# Test camera
libcamera-still -o test.jpg

# Check permissions
sudo usermod -a -G video $USER
```

**Problem: GPIO permissions**
```bash
sudo usermod -a -G gpio $USER
sudo reboot
```

**Problem: OCR not detecting plates**
- Improve lighting
- Adjust camera angle
- Use higher resolution
- Clean test images

**Problem: Cannot connect to backend**
```bash
# Test connectivity
ping YOUR_BACKEND_IP

# Test API
curl http://YOUR_BACKEND_IP:5000/health

# Check firewall
sudo ufw status
sudo ufw allow 5000
```

---

## Part 7: Security Hardening

### 7.1 Enable HTTPS

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 7.2 Add API Authentication

See `docs/SECURITY.md` for JWT implementation.

### 7.3 Firewall Configuration

```bash
# Backend server
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5000
sudo ufw enable
```

---

## Part 8: Monitoring

### 8.1 View Logs

```bash
# Backend logs
sudo journalctl -u vehicle-pass -f

# Raspberry Pi logs
sudo journalctl -u vehicle-controller -f
```

### 8.2 Setup Monitoring (Optional)

Install monitoring tools:
- CloudWatch (AWS)
- Prometheus + Grafana
- Uptime Robot

---

## Success Checklist

- [ ] AWS DynamoDB table created
- [ ] Backend server running
- [ ] Frontend accessible
- [ ] Can register vehicles via web form
- [ ] Raspberry Pi hardware connected
- [ ] All sensors tested individually
- [ ] Main controller running
- [ ] End-to-end test successful
- [ ] Auto-start enabled
- [ ] Monitoring configured

---

## Next Steps

1. Register your vehicles
2. Monitor system performance
3. Adjust detection thresholds
4. Implement additional features
5. Scale as needed

For detailed API documentation, see `docs/API.md`
For security best practices, see `docs/SECURITY.md`
