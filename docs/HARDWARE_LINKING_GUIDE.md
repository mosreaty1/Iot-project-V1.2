# Hardware Linking & Connection Guide

## Complete Step-by-Step Guide for Connecting IoT Components

This guide will walk you through physically connecting all hardware components to your Raspberry Pi and integrating them with the Vehicle Pass Registration System.

---

## 📦 Required Components

### Main Components:
1. **Raspberry Pi** (Model 3B+ or 4 recommended)
2. **Raspberry Pi Camera Module** (V2 or compatible)
3. **HC-SR04 Ultrasonic Sensor**
4. **16x2 LCD Display** (with I2C adapter or standard 16-pin)
5. **LEDs** (1 Red, 1 Green for traffic light)
6. **SG90 Servo Motor** (for barrier gate)
7. **Power Supply** (5V 3A for Raspberry Pi)

### Additional Materials:
- Jumper wires (Male-to-Female, Male-to-Male)
- Breadboard (830 points recommended)
- Resistors:
  - 2x 220Ω (for LEDs)
  - 1x 1kΩ (voltage divider for ultrasonic sensor)
  - 1x 2kΩ (voltage divider for ultrasonic sensor)
- MicroSD card (16GB+ with Raspberry Pi OS)
- Optional: Soldering iron & solder for permanent connections

---

## 🔌 Step 1: Prepare Your Raspberry Pi

### 1.1 Install Operating System
```bash
# Download Raspberry Pi Imager
# Flash Raspberry Pi OS (32-bit or 64-bit)
# Insert SD card into Raspberry Pi
```

### 1.2 Enable Required Interfaces
```bash
# Run Raspberry Pi Configuration
sudo raspi-config

# Enable:
# - Interface Options → Camera → Enable
# - Interface Options → I2C → Enable (if using I2C LCD)
# - Interface Options → SSH → Enable (for remote access)

# Reboot
sudo reboot
```

### 1.3 Install Required Software
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python dependencies
sudo apt-get install -y python3-pip python3-opencv
sudo apt-get install -y python3-rpi.gpio python3-picamera

# Install Tesseract OCR
sudo apt-get install -y tesseract-ocr libtesseract-dev

# Install project dependencies
cd /home/pi/Iot-project-V1.2
pip3 install -r requirements.txt
```

---

## 🔧 Step 2: Connect Components One by One

### 2.1 Camera Module Connection

**Physical Connection:**
1. Locate the CSI camera port on Raspberry Pi (between HDMI and audio jack)
2. Gently pull up the plastic clip
3. Insert ribbon cable with **blue side facing audio jack**
4. Push down the plastic clip to secure

**Testing:**
```bash
# Test camera
raspistill -o test.jpg

# If successful, you'll see test.jpg in current directory
ls -lh test.jpg
```

**Wiring Diagram:**
```
Raspberry Pi CSI Port
    ↓
[Ribbon Cable]
    ↓
Camera Module
```

---

### 2.2 Ultrasonic Sensor (HC-SR04) Connection

**⚠️ IMPORTANT:** The HC-SR04 outputs 5V on ECHO pin, but Raspberry Pi GPIO pins are 3.3V tolerant. **You MUST use a voltage divider!**

**Pin Connections:**
```
HC-SR04 Sensor          Raspberry Pi
─────────────────────────────────────
VCC       →             5V (Pin 2 or 4)
GND       →             GND (Pin 6)
TRIG      →             GPIO 23 (Pin 16)
ECHO      →             [Voltage Divider] → GPIO 24 (Pin 18)
```

**Voltage Divider Circuit:**
```
ECHO pin (5V)
    │
    ├─── 2kΩ Resistor ───┐
    │                     ├──→ GPIO 24 (3.3V safe)
    └─── 1kΩ Resistor ───┤
                          │
                         GND
```

**Breadboard Setup:**
1. Place HC-SR04 on breadboard
2. Connect VCC to 5V rail (red rail)
3. Connect GND to GND rail (blue rail)
4. Connect TRIG directly to GPIO 23
5. For ECHO pin:
   - Connect ECHO to one end of 2kΩ resistor
   - Connect other end of 2kΩ to GPIO 24
   - Connect a 1kΩ resistor from GPIO 24 to GND

**Testing:**
```bash
# Create test script
nano test_ultrasonic.py
```

```python
import RPi.GPIO as GPIO
import time

TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

try:
    while True:
        GPIO.output(TRIG, False)
        time.sleep(0.1)

        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        print(f"Distance: {distance} cm")
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
```

```bash
# Run test
python3 test_ultrasonic.py

# Expected: Distance readings in cm (wave hand in front to test)
```

---

### 2.3 LCD Display Connection

**Option A: I2C LCD (Easier - Recommended)**

**Pin Connections:**
```
I2C LCD Module          Raspberry Pi
─────────────────────────────────────
VCC       →             5V (Pin 2)
GND       →             GND (Pin 6)
SDA       →             GPIO 2/SDA (Pin 3)
SCL       →             GPIO 3/SCL (Pin 5)
```

**Testing:**
```bash
# Detect I2C address
sudo i2cdetect -y 1

# Should show address (usually 0x27 or 0x3F)

# Install I2C LCD library
pip3 install RPLCD

# Test script
python3 -c "
from RPLCD.i2c import CharLCD
lcd = CharLCD('PCF8574', 0x27)
lcd.write_string('Hello World!')
"
```

**Option B: Standard 16-Pin LCD (More Wiring)**

**Pin Connections (4-bit mode):**
```
LCD Pin    Function    Raspberry Pi
───────────────────────────────────────
1  VSS     GND         GND (Pin 6)
2  VDD     +5V         5V (Pin 2)
3  V0      Contrast    Middle pin of 10kΩ pot
4  RS      Register    GPIO 7 (Pin 26)
5  RW      Read/Write  GND (always write)
6  EN      Enable      GPIO 8 (Pin 24)
7  D0      Data 0      Not connected
8  D1      Data 1      Not connected
9  D2      Data 2      Not connected
10 D3      Data 3      Not connected
11 D4      Data 4      GPIO 25 (Pin 22)
12 D5      Data 5      GPIO 24 (Pin 18)
13 D6      Data 6      GPIO 23 (Pin 16)
14 D7      Data 7      GPIO 18 (Pin 12)
15 A       Backlight+  5V (via 220Ω resistor)
16 K       Backlight-  GND
```

**Testing:**
```bash
# Install library
pip3 install RPLCD

# Test script
nano test_lcd.py
```

```python
from RPLCD.gpio import CharLCD
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

lcd = CharLCD(
    pin_rs=7, pin_e=8,
    pins_data=[25, 24, 23, 18],
    numbering_mode=GPIO.BCM,
    cols=16, rows=2
)

lcd.write_string('System Ready!')
lcd.cursor_pos = (1, 0)
lcd.write_string('Test Success')
```

```bash
python3 test_lcd.py
```

---

### 2.4 Traffic Light LEDs Connection

**Pin Connections:**
```
Component               Raspberry Pi
─────────────────────────────────────
Red LED (+)   →  220Ω resistor  →  GPIO 17 (Pin 11)
Red LED (-)   →  GND (Pin 9)

Green LED (+) →  220Ω resistor  →  GPIO 27 (Pin 13)
Green LED (-) →  GND (Pin 14)
```

**LED Polarity:**
- Long leg = Anode (+) → connects to GPIO via resistor
- Short leg = Cathode (-) → connects to GND

**Breadboard Setup:**
1. Insert Red LED in breadboard
2. Connect long leg to GPIO 17 through 220Ω resistor
3. Connect short leg to GND rail
4. Repeat for Green LED with GPIO 27

**Testing:**
```bash
nano test_leds.py
```

```python
import RPi.GPIO as GPIO
import time

RED_PIN = 17
GREEN_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)

try:
    print("Testing Red LED...")
    GPIO.output(RED_PIN, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(RED_PIN, GPIO.LOW)

    print("Testing Green LED...")
    GPIO.output(GREEN_PIN, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(GREEN_PIN, GPIO.LOW)

    print("Both LEDs blinking...")
    for _ in range(5):
        GPIO.output(RED_PIN, GPIO.HIGH)
        GPIO.output(GREEN_PIN, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(RED_PIN, GPIO.LOW)
        GPIO.output(GREEN_PIN, GPIO.HIGH)
        time.sleep(0.5)

    GPIO.output(GREEN_PIN, GPIO.LOW)
    print("Test complete!")

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
```

```bash
python3 test_leds.py
```

---

### 2.5 Servo Motor (Barrier Gate) Connection

**Pin Connections:**
```
SG90 Servo              Raspberry Pi
─────────────────────────────────────
Brown/Black (GND) →     GND (Pin 20)
Red (VCC)         →     5V (Pin 4)
Orange/Yellow     →     GPIO 22 (Pin 15)
```

**⚠️ Power Consideration:**
- Small servos (SG90) can run from Pi's 5V
- For larger servos, use external 5V power supply
- Share GND between Pi and external supply

**Testing:**
```bash
nano test_servo.py
```

```python
import RPi.GPIO as GPIO
import time

SERVO_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# 50Hz PWM
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def set_angle(angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

try:
    print("Testing servo: 0° (barrier closed)")
    set_angle(0)
    time.sleep(2)

    print("Testing servo: 90° (barrier open)")
    set_angle(90)
    time.sleep(2)

    print("Testing servo: 0° (barrier closed)")
    set_angle(0)
    time.sleep(2)

    print("Test complete!")

except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()
```

```bash
python3 test_servo.py
```

---

## 🔗 Step 3: Complete Wiring Diagram

### Full Pin Layout:

```
Raspberry Pi GPIO Pinout:
═══════════════════════════════════════════════════

   3.3V  (1)  (2)  5V           ← Power rails
  SDA.1  (3)  (4)  5V           ← I2C (LCD if using I2C)
  SCL.1  (5)  (6)  GND          ← I2C, Ground
  GPIO7  (7)  (8)  GPIO14       ← LCD RS
    GND  (9) (10)  GPIO15
GPIO17 (11) (12)  GPIO18        ← Red LED, LCD D7
GPIO27 (13) (14)  GND           ← Green LED, Ground
GPIO22 (15) (16)  GPIO23        ← Servo, Ultrasonic TRIG / LCD D6
   3.3V (17) (18)  GPIO24       ← Ultrasonic ECHO / LCD D5
GPIO10 (19) (20)  GND           ← Ground
 GPIO9 (21) (22)  GPIO25        ← LCD D4
GPIO11 (23) (24)  GPIO8         ← LCD EN
    GND (25) (26)  GPIO7        ← Ground, LCD RS

[Additional pins continue...]
```

### Connection Summary Table:

| Component | Pin/Wire | Raspberry Pi GPIO | Physical Pin |
|-----------|----------|-------------------|--------------|
| **Camera** | Ribbon Cable | CSI Port | CSI Port |
| **Ultrasonic VCC** | Red | 5V | Pin 2 |
| **Ultrasonic GND** | Black | GND | Pin 6 |
| **Ultrasonic TRIG** | Yellow | GPIO 23 | Pin 16 |
| **Ultrasonic ECHO** | Orange | GPIO 24 (via divider) | Pin 18 |
| **LCD VCC** | Red | 5V | Pin 2 |
| **LCD GND** | Black | GND | Pin 6 |
| **LCD SDA** | Blue | GPIO 2 (SDA) | Pin 3 |
| **LCD SCL** | Green | GPIO 3 (SCL) | Pin 5 |
| **Red LED (+)** | Red | GPIO 17 (via 220Ω) | Pin 11 |
| **Red LED (-)** | Black | GND | Pin 9 |
| **Green LED (+)** | Green | GPIO 27 (via 220Ω) | Pin 13 |
| **Green LED (-)** | Black | GND | Pin 14 |
| **Servo GND** | Brown | GND | Pin 20 |
| **Servo VCC** | Red | 5V | Pin 4 |
| **Servo Signal** | Orange | GPIO 22 | Pin 15 |

---

## 🔧 Step 4: Project Software Integration

### 4.1 Clone/Copy Project to Raspberry Pi

```bash
# If project not already on Pi:
cd /home/pi
git clone https://github.com/mosreaty1/Iot-project-V1.2.git
cd Iot-project-V1.2

# Or transfer via SCP from your computer:
# scp -r Iot-project-V1.2/ pi@<raspberry-pi-ip>:/home/pi/
```

### 4.2 Configure Backend API URL

```bash
# Edit Raspberry Pi configuration
nano raspberry_pi/config/settings.py
```

**Update line 5:**
```python
# Replace with your backend server IP address
'API_URL': 'http://192.168.1.100:5000'  # Example: your computer's IP
```

To find your backend server IP:
```bash
# On Windows (from Command Prompt):
ipconfig

# On Linux/Mac:
ifconfig
# or
ip addr show
```

### 4.3 Install Project Dependencies

```bash
cd /home/pi/Iot-project-V1.2

# Install Python dependencies
pip3 install -r requirements.txt

# Additional Raspberry Pi specific packages
pip3 install RPi.GPIO
pip3 install picamera
pip3 install opencv-python-headless
pip3 install pytesseract
pip3 install RPLCD
```

### 4.4 Verify Configuration

```bash
# Check settings.py configuration
cat raspberry_pi/config/settings.py
```

**Verify all GPIO pins match your wiring:**
```python
'ULTRASONIC_TRIGGER_PIN': 23,
'ULTRASONIC_ECHO_PIN': 24,
'LCD_RS_PIN': 7,
'LCD_EN_PIN': 8,
'LCD_D4_PIN': 25,
'LCD_D5_PIN': 24,
'LCD_D6_PIN': 23,
'LCD_D7_PIN': 18,
'TRAFFIC_RED_PIN': 17,
'TRAFFIC_GREEN_PIN': 27,
'BARRIER_SERVO_PIN': 22,
```

---

## ✅ Step 5: Test Complete System

### 5.1 Test Each Module Individually

```bash
cd /home/pi/Iot-project-V1.2/raspberry_pi

# Test camera
python3 -c "from modules.camera import CameraModule; cam = CameraModule(); print('Camera OK')"

# Test ultrasonic
python3 -c "from modules.ultrasonic import UltrasonicSensor; sensor = UltrasonicSensor(); print(f'Distance: {sensor.get_distance()}cm')"

# Test LCD
python3 -c "from modules.lcd_display import LCDDisplay; lcd = LCDDisplay(); lcd.show_message('Test', 'Success'); print('LCD OK')"

# Test traffic light
python3 -c "from modules.traffic_light import TrafficLight; light = TrafficLight(); light.green_on(); print('Traffic Light OK'); light.cleanup()"

# Test barrier
python3 -c "from modules.barrier import BarrierControl; barrier = BarrierControl(); barrier.open_barrier(); barrier.close_barrier(); print('Barrier OK'); barrier.cleanup()"
```

### 5.2 Start Backend Server

**On your backend server (computer):**
```bash
cd backend
python app.py

# Should see:
# * Running on http://0.0.0.0:5000
```

### 5.3 Test Backend Connectivity from Raspberry Pi

```bash
# Test health endpoint
curl http://192.168.1.100:5000/health

# Expected response:
# {"status": "healthy"}

# Test from Python
python3 -c "import requests; print(requests.get('http://192.168.1.100:5000/health').json())"
```

### 5.4 Register Test Vehicle

**Open browser on any device:**
```
http://192.168.1.100:8080/index.html
```

Register a test vehicle:
- Name: Test User
- Plate: ABC123
- Car Type: Sedan
- Email: test@example.com
- Phone: 1234567890
- Passes: 10

### 5.5 Run Main System

```bash
cd /home/pi/Iot-project-V1.2
python3 raspberry_pi/main.py
```

**Expected output:**
```
Vehicle Access Control System Starting...
Initializing hardware modules...
✓ Camera module initialized
✓ Ultrasonic sensor initialized
✓ LCD display initialized
✓ Traffic light initialized
✓ Barrier control initialized
System ready. Waiting for vehicles...
```

### 5.6 Test Access Control

1. Hold a piece of paper with "ABC123" in front of camera
2. Move object within 50cm of ultrasonic sensor
3. Watch for:
   - LCD shows "Scanning..."
   - LCD shows "Welcome Test User"
   - Green LED turns ON
   - Servo rotates (barrier opens)
   - After 5 seconds, barrier closes
   - Red LED turns ON

---

## 🚨 Troubleshooting

### Camera Not Working
```bash
# Check if camera is detected
vcgencmd get_camera

# Should show: supported=1 detected=1

# If not, check:
# 1. Ribbon cable is fully inserted
# 2. Blue side faces audio jack
# 3. Camera is enabled in raspi-config
```

### Ultrasonic Sensor Not Responding
```bash
# Common issues:
# 1. Missing voltage divider on ECHO pin → will damage Pi!
# 2. Loose jumper wires
# 3. Incorrect GPIO pins in code

# Check connections:
# VCC → 5V (red rail)
# GND → GND (blue rail)
# TRIG → GPIO 23 directly
# ECHO → GPIO 24 via voltage divider
```

### LCD Display Blank/Not Working
```bash
# For I2C LCD:
# Check I2C address
sudo i2cdetect -y 1

# Adjust contrast (potentiometer on back of LCD)
# Turn clockwise/counter-clockwise

# Verify power:
# VCC → 5V
# GND → GND
```

### LEDs Not Lighting
```bash
# Check:
# 1. LED polarity (long leg = positive)
# 2. Resistor value (220Ω, color: Red-Red-Brown)
# 3. GPIO pins correct
# 4. Common ground connected

# Test with direct connection:
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.OUT); GPIO.output(17, GPIO.HIGH); input('Press Enter'); GPIO.cleanup()"
```

### Servo Not Moving
```bash
# Check:
# 1. Power supply adequate (5V, sufficient current)
# 2. Signal wire on correct GPIO (22)
# 3. Common ground between Pi and servo
# 4. Servo not jammed mechanically

# Test servo directly:
python3 test_servo.py
```

### Cannot Connect to Backend
```bash
# Check:
# 1. Backend server is running
# 2. Firewall allows port 5000
# 3. Correct IP address in settings.py
# 4. Both devices on same network

# Test connectivity:
ping 192.168.1.100

# Test port:
curl http://192.168.1.100:5000/health
```

### GPIO Warnings/Cleanup
```bash
# If you see "GPIO already in use" warnings:
# This happens when previous script didn't cleanup

# Solution: Reset GPIO
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.cleanup()"
```

---

## 🎯 Step 6: Making Connections Permanent

### For Prototyping (Breadboard)
- Use quality jumper wires
- Secure connections with tape if needed
- Label wires with tape and marker

### For Permanent Installation

**Option 1: Soldering to Prototype Board**
1. Transfer breadboard design to perma-proto board
2. Solder all connections
3. Use female headers for GPIO connection
4. Add screw terminals for external components

**Option 2: Custom PCB**
1. Design PCB using KiCad or EasyEDA
2. Order PCB fabrication
3. Solder components
4. Create HAT that sits on top of Raspberry Pi

**Option 3: Shield/HAT**
1. Use commercial HAT with screw terminals
2. Wire components to terminals
3. More reliable for vibration/movement

---

## 📋 Final Checklist

- [ ] Raspberry Pi OS installed and updated
- [ ] Camera enabled and tested
- [ ] All GPIO interfaces enabled (I2C, Camera)
- [ ] Voltage divider for ultrasonic sensor installed
- [ ] All components connected and tested individually
- [ ] Project code copied to Raspberry Pi
- [ ] Backend API URL configured correctly
- [ ] Dependencies installed
- [ ] Backend server running
- [ ] Test vehicle registered in system
- [ ] Main system runs without errors
- [ ] End-to-end access control tested successfully
- [ ] Connections secured for long-term use

---

## 🚀 Auto-Start on Boot (Optional)

To make the system start automatically when Raspberry Pi boots:

```bash
# Create systemd service
sudo nano /etc/systemd/system/vehicle-access.service
```

**Add content:**
```ini
[Unit]
Description=Vehicle Access Control System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Iot-project-V1.2
ExecStart=/usr/bin/python3 /home/pi/Iot-project-V1.2/raspberry_pi/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable vehicle-access.service
sudo systemctl start vehicle-access.service

# Check status:
sudo systemctl status vehicle-access.service

# View logs:
sudo journalctl -u vehicle-access.service -f
```

---

## 📞 Support

If you encounter issues:
1. Check troubleshooting section above
2. Verify all connections match wiring diagram
3. Test each component individually
4. Check logs for error messages
5. Ensure backend server is accessible

**Additional Resources:**
- `docs/SETUP_GUIDE.md` - Complete project setup
- `docs/WIRING_DIAGRAM.md` - Detailed wiring schematics
- `docs/API.md` - Backend API documentation
- `README.md` - Project overview

---

**Good luck with your IoT project! 🎉**
