"""
Ultrasonic Sensor Module (HC-SR04)
Measures distance to detect vehicle presence
"""
import time
import logging

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available, using mock sensor")

logger = logging.getLogger(__name__)


class UltrasonicSensor:
    """HC-SR04 Ultrasonic Distance Sensor"""

    def __init__(self, trigger_pin=23, echo_pin=24):
        """Initialize ultrasonic sensor"""
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.trigger_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            GPIO.output(self.trigger_pin, GPIO.LOW)
            time.sleep(0.1)
            self.mock_mode = False
            logger.info(f"Ultrasonic sensor initialized (Trigger: {trigger_pin}, Echo: {echo_pin})")
        else:
            self.mock_mode = True
            logger.warning("Using mock ultrasonic sensor")

    def get_distance(self):
        """Get distance measurement in centimeters"""
        if self.mock_mode:
            return self._mock_distance()

        try:
            # Send trigger pulse
            GPIO.output(self.trigger_pin, GPIO.HIGH)
            time.sleep(0.00001)  # 10 microseconds
            GPIO.output(self.trigger_pin, GPIO.LOW)

            # Wait for echo
            timeout = time.time() + 0.5  # 500ms timeout

            # Wait for echo start
            while GPIO.input(self.echo_pin) == GPIO.LOW:
                pulse_start = time.time()
                if pulse_start > timeout:
                    logger.warning("Ultrasonic timeout (no echo start)")
                    return 999  # Return large distance on timeout

            # Wait for echo end
            while GPIO.input(self.echo_pin) == GPIO.HIGH:
                pulse_end = time.time()
                if pulse_end > timeout:
                    logger.warning("Ultrasonic timeout (no echo end)")
                    return 999

            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150  # Speed of sound / 2
            distance = round(distance, 2)

            return distance

        except Exception as e:
            logger.error(f"Ultrasonic sensor error: {e}")
            return 999

    def _mock_distance(self):
        """Mock distance for testing (simulates vehicle presence randomly)"""
        import random
        # Randomly return close or far distance
        return random.choice([20, 30, 40, 200, 200, 200])  # More often far

    def cleanup(self):
        """Cleanup GPIO"""
        if GPIO_AVAILABLE and not self.mock_mode:
            GPIO.cleanup([self.trigger_pin, self.echo_pin])
            logger.info("Ultrasonic sensor GPIO cleaned up")
