"""
Raspberry Pi Configuration Settings
"""

RPI_CONFIG = {
    # Backend API
    'API_URL': 'http://YOUR_BACKEND_SERVER_IP:5000',

    # GPIO Pin Configuration (BCM numbering)
    # Ultrasonic Sensor (HC-SR04)
    'ULTRASONIC_TRIGGER_PIN': 23,
    'ULTRASONIC_ECHO_PIN': 24,

    # LCD Display (16x2 with HD44780)
    'LCD_RS_PIN': 7,
    'LCD_EN_PIN': 8,
    'LCD_D4_PIN': 25,
    'LCD_D5_PIN': 24,
    'LCD_D6_PIN': 23,
    'LCD_D7_PIN': 18,

    # Traffic Light LEDs
    'TRAFFIC_RED_PIN': 17,
    'TRAFFIC_GREEN_PIN': 27,

    # Barrier Servo Motor
    'BARRIER_SERVO_PIN': 22,

    # Detection Settings
    'DETECTION_THRESHOLD_CM': 50,  # Trigger when vehicle within 50cm
    'COOLDOWN_TIME_SECONDS': 10,   # Wait 10s between detections
    'BARRIER_OPEN_TIME_SECONDS': 5, # Keep barrier open for 5s
}
