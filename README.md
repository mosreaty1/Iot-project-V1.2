# Vehicle Pass Registration System

An IoT-based automated vehicle access control system using Raspberry Pi, AWS DynamoDB, and cloud integration.

## System Overview

This project implements a smart parking/gate access control system that:
- Detects vehicles using ultrasonic sensors
- Captures and recognizes license plates using camera + OCR
- Verifies vehicle registration against AWS DynamoDB
- Controls barrier access with traffic lights
- Displays welcome messages on LCD with remaining passes
- Provides web-based registration interface

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Web Form  │─────▶│ Flask Backend│─────▶│  DynamoDB   │
│  (Frontend) │      │   (AWS EC2)  │      │   (AWS)     │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Raspberry Pi │
                     │  Controller  │
                     └──────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼────┐      ┌───────▼──────┐    ┌──────▼─────┐
    │ Camera │      │   Ultrasonic │    │    LCD     │
    │ + OCR  │      │    Sensor    │    │  Display   │
    └────────┘      └──────────────┘    └────────────┘
        │                   │                   │
        │           ┌───────▼──────┐    ┌──────▼─────┐
        └──────────▶│Traffic Light │    │  Barrier   │
                    │  (Red/Green) │    │  (Servo)   │
                    └──────────────┘    └────────────┘
```

## Hardware Requirements

### Raspberry Pi Setup
- Raspberry Pi 4 (recommended) or Pi 3B+
- MicroSD card (32GB+)
- Power supply (5V/3A)

### Sensors & Actuators
- **Camera**: Pi Camera Module V2 or USB webcam
- **Ultrasonic Sensor**: HC-SR04
- **LCD Display**: 16x2 LCD with HD44780 controller
- **Traffic Light**: Red and Green LEDs (or LED modules)
- **Barrier**: SG90 or MG995 servo motor
- **Breadboard and jumper wires**

### GPIO Pin Connections (BCM numbering)

| Component | Pin | GPIO |
|-----------|-----|------|
| Ultrasonic Trigger | - | GPIO 23 |
| Ultrasonic Echo | - | GPIO 24 |
| LCD RS | - | GPIO 7 |
| LCD EN | - | GPIO 8 |
| LCD D4-D7 | - | GPIO 25,24,23,18 |
| Red LED | - | GPIO 17 |
| Green LED | - | GPIO 27 |
| Servo Motor | - | GPIO 22 |

## Software Requirements

- Python 3.9+
- Node.js (optional, for alternative backend)
- AWS Account (for DynamoDB and S3)

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd IOT-PROJECT-v2
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
nano .env  # Edit with your AWS credentials and settings
```

### 3. AWS Configuration

#### Create DynamoDB Table
The application will auto-create the table on first run, or create manually:

```bash
# Using AWS CLI
aws dynamodb create-table \
    --table-name VehiclePassRegistrations \
    --attribute-definitions AttributeName=plate_number,AttributeType=S \
    --key-schema AttributeName=plate_number,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

#### IAM Permissions
Ensure your IAM user/role has these permissions:
- `dynamodb:CreateTable`
- `dynamodb:PutItem`
- `dynamodb:GetItem`
- `dynamodb:UpdateItem`
- `dynamodb:Scan`
- `dynamodb:Query`

### 4. Raspberry Pi Setup

```bash
# On Raspberry Pi
cd raspberry_pi
pip install -r requirements.txt

# Install Tesseract OCR
sudo apt-get update
sudo apt-get install tesseract-ocr -y

# Configure settings
nano config/settings.py  # Update API_URL with your backend server IP
```

### 5. Frontend Setup

Update API URL in frontend files:
```javascript
// In frontend/index.html and frontend/admin.html
const API_URL = 'http://YOUR_BACKEND_IP:5000/api';
```

Serve frontend files using any web server:
```bash
# Simple Python server
cd frontend
python -m http.server 8080
```

Or use Nginx/Apache for production.

## Usage

### 1. Start Backend Server

```bash
# Development
python backend/app.py

# Production (with Gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### 2. Start Raspberry Pi Controller

```bash
cd raspberry_pi
python main.py
```

### 3. Register Vehicles

Open browser and navigate to:
```
http://YOUR_SERVER_IP:8080
```

Fill in:
- Name
- Plate Number (e.g., ABC-1234)
- Car Type
- Email
- Phone Number
- Number of passes (5-10)

### 4. Access Control Flow

1. Vehicle approaches gate
2. Ultrasonic sensor detects presence (< 50cm)
3. Camera captures license plate image
4. OCR extracts plate number
5. System verifies with backend API
6. If authorized:
   - LCD displays: "Welcome [Name], [X] time to pass"
   - Green light turns on
   - Barrier opens
   - Pass count decrements
7. If denied:
   - LCD displays: "Access Denied"
   - Red light blinks
   - Barrier stays closed

## API Endpoints

### Registration
```http
POST /api/register
Content-Type: application/json

{
  "name": "John Doe",
  "plate_number": "ABC1234",
  "car_type": "Sedan",
  "email": "john@example.com",
  "phone_number": "+20 1234567890",
  "passes": 5
}
```

### Vehicle Verification
```http
POST /api/verify
Content-Type: application/json

{
  "plate_number": "ABC1234"
}
```

### Deduct Pass
```http
POST /api/deduct-pass
Content-Type: application/json

{
  "plate_number": "ABC1234"
}
```

### Get Vehicle Info
```http
GET /api/vehicle/{plate_number}
```

### List All Vehicles
```http
GET /api/vehicles
```

### Add Passes
```http
POST /api/add-passes
Content-Type: application/json

{
  "plate_number": "ABC1234",
  "passes": 5
}
```

## Configuration

### Backend (.env)
```env
SECRET_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
DYNAMODB_TABLE_NAME=VehiclePassRegistrations
```

### Raspberry Pi (config/settings.py)
```python
RPI_CONFIG = {
    'API_URL': 'http://YOUR_SERVER_IP:5000',
    'DETECTION_THRESHOLD_CM': 50,
    'COOLDOWN_TIME_SECONDS': 10,
    'BARRIER_OPEN_TIME_SECONDS': 5,
    # GPIO pin configurations...
}
```

## Admin Dashboard

Access the admin dashboard at:
```
http://YOUR_SERVER_IP:8080/admin.html
```

Features:
- View all registered vehicles
- Monitor pass usage statistics
- Real-time updates
- Filter by status (active/low/empty)

## Troubleshooting

### Camera Issues
```bash
# Test camera
libcamera-still -o test.jpg

# Enable camera interface
sudo raspi-config
# Interface Options -> Camera -> Enable
```

### GPIO Permissions
```bash
sudo usermod -a -G gpio $USER
sudo reboot
```

### DynamoDB Connection Issues
- Verify AWS credentials
- Check IAM permissions
- Ensure correct region
- Test with AWS CLI: `aws dynamodb list-tables`

### OCR Not Detecting Plates
- Ensure good lighting
- Adjust camera angle
- Clean camera lens
- Try different OCR engines (EasyOCR vs Tesseract)

## Development

### Mock Mode Testing
The system includes mock modes for testing without hardware:
```python
# All hardware modules detect missing GPIO and switch to mock mode
# Useful for development on non-RPi systems
```

### Running Tests
```bash
# Backend tests
python -m pytest tests/

# Hardware module tests
cd raspberry_pi
python -m pytest tests/
```

## Security Considerations

1. **API Security**: Add authentication (JWT tokens)
2. **HTTPS**: Use SSL certificates in production
3. **Input Validation**: Already implemented server-side
4. **Rate Limiting**: Add Flask-Limiter for API protection
5. **AWS Credentials**: Never commit to repository

## Future Enhancements

- [ ] Mobile app for registration
- [ ] Email/SMS notifications
- [ ] Payment integration
- [ ] Multiple barrier support
- [ ] Analytics dashboard
- [ ] Face recognition
- [ ] Automated gate for pedestrians
- [ ] Integration with parking management systems

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Email: support@example.com

## Contributors

- Your Name - Initial work

## Acknowledgments

- OpenCV for image processing
- EasyOCR for license plate recognition
- AWS for cloud infrastructure
- Flask framework
