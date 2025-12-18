"""
Raspberry Pi Main Controller for Vehicle Pass Registration System
Handles hardware integration and communication with backend API
"""
import time
import requests
import logging
from datetime import datetime
import sys
import os

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.camera import CameraModule
from modules.ultrasonic import UltrasonicSensor
from modules.lcd_display import LCDDisplay
from modules.traffic_light import TrafficLight
from modules.barrier import BarrierControl
from config.settings import RPI_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VehicleAccessController:
    """Main controller for vehicle access system"""

    def __init__(self):
        """Initialize all hardware modules"""
        logger.info("Initializing Vehicle Access Controller...")

        # Initialize hardware modules
        self.camera = CameraModule()
        self.ultrasonic = UltrasonicSensor(
            trigger_pin=RPI_CONFIG['ULTRASONIC_TRIGGER_PIN'],
            echo_pin=RPI_CONFIG['ULTRASONIC_ECHO_PIN']
        )
        self.lcd = LCDDisplay(
            rs_pin=RPI_CONFIG['LCD_RS_PIN'],
            en_pin=RPI_CONFIG['LCD_EN_PIN'],
            d4_pin=RPI_CONFIG['LCD_D4_PIN'],
            d5_pin=RPI_CONFIG['LCD_D5_PIN'],
            d6_pin=RPI_CONFIG['LCD_D6_PIN'],
            d7_pin=RPI_CONFIG['LCD_D7_PIN']
        )
        self.traffic_light = TrafficLight(
            red_pin=RPI_CONFIG['TRAFFIC_RED_PIN'],
            green_pin=RPI_CONFIG['TRAFFIC_GREEN_PIN']
        )
        self.barrier = BarrierControl(
            servo_pin=RPI_CONFIG['BARRIER_SERVO_PIN']
        )

        # Backend API URL
        self.api_url = RPI_CONFIG['API_URL']

        # Detection parameters
        self.detection_threshold = RPI_CONFIG['DETECTION_THRESHOLD_CM']
        self.cooldown_time = RPI_CONFIG['COOLDOWN_TIME_SECONDS']
        self.last_detection_time = 0

        logger.info("Vehicle Access Controller initialized successfully")

    def verify_vehicle_with_backend(self, plate_number):
        """Verify vehicle with backend API"""
        try:
            response = requests.post(
                f"{self.api_url}/api/verify",
                json={'plate_number': plate_number},
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Backend verification failed: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            return None

    def deduct_pass_from_backend(self, plate_number):
        """Deduct pass from backend"""
        try:
            response = requests.post(
                f"{self.api_url}/api/deduct-pass",
                json={'plate_number': plate_number},
                timeout=5
            )

            if response.status_code == 200:
                return True
            else:
                logger.error(f"Pass deduction failed: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            return False

    def grant_access(self, name, remaining_passes):
        """Grant access to vehicle"""
        logger.info(f"Granting access to {name}")

        # Display welcome message
        self.lcd.display_message(
            f"Welcome {name}",
            f"{remaining_passes} time to pass"
        )

        # Green light
        self.traffic_light.green()

        # Open barrier
        self.barrier.open()

        # Keep barrier open for configured time
        time.sleep(RPI_CONFIG['BARRIER_OPEN_TIME_SECONDS'])

        # Close barrier
        self.barrier.close()

        # Red light
        self.traffic_light.red()

        # Clear LCD after delay
        time.sleep(2)
        self.lcd.clear()

    def deny_access(self, message="Access Denied"):
        """Deny access to vehicle"""
        logger.info(f"Denying access: {message}")

        # Display denied message
        self.lcd.display_message(
            "Access Denied",
            message
        )

        # Red light (blink)
        for _ in range(3):
            self.traffic_light.off()
            time.sleep(0.3)
            self.traffic_light.red()
            time.sleep(0.3)

        # Clear LCD after delay
        time.sleep(3)
        self.lcd.clear()

    def process_vehicle(self):
        """Process detected vehicle"""
        logger.info("Vehicle detected, processing...")

        # Show scanning message
        self.lcd.display_message("Scanning...", "Please wait")

        # Capture image
        image_path = self.camera.capture_image()

        if not image_path:
            logger.error("Failed to capture image")
            self.deny_access("Camera Error")
            return

        # Perform license plate recognition
        plate_number = self.camera.recognize_plate(image_path)

        if not plate_number:
            logger.error("Failed to recognize plate number")
            self.deny_access("Plate Not Read")
            return

        logger.info(f"Plate recognized: {plate_number}")

        # Verify with backend
        verification_result = self.verify_vehicle_with_backend(plate_number)

        if not verification_result:
            self.deny_access("System Error")
            return

        if verification_result.get('authorized'):
            name = verification_result.get('name', 'Guest')
            remaining_passes = verification_result.get('remaining_passes', 0)

            # Deduct pass from backend
            if self.deduct_pass_from_backend(plate_number):
                # Access granted
                self.grant_access(name, remaining_passes - 1)
            else:
                self.deny_access("System Error")
        else:
            # Access denied
            message = verification_result.get('message', 'Not Registered')
            self.deny_access(message)

    def run(self):
        """Main loop - monitor for vehicles and process them"""
        logger.info("Starting vehicle access control system...")

        # Initial state
        self.traffic_light.red()
        self.lcd.display_message("System Ready", "")

        time.sleep(2)
        self.lcd.clear()

        try:
            while True:
                # Check for vehicle presence
                distance = self.ultrasonic.get_distance()

                # Vehicle detected
                if distance < self.detection_threshold:
                    current_time = time.time()

                    # Check cooldown period
                    if current_time - self.last_detection_time > self.cooldown_time:
                        self.last_detection_time = current_time
                        self.process_vehicle()

                # Small delay to prevent CPU overload
                time.sleep(0.5)

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        self.lcd.clear()
        self.traffic_light.off()
        self.barrier.close()
        self.camera.cleanup()
        self.ultrasonic.cleanup()
        logger.info("Cleanup complete")


if __name__ == '__main__':
    controller = VehicleAccessController()
    controller.run()
