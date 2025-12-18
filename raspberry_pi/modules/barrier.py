"""
Barrier Control Module (Servo Motor)
Controls parking barrier/gate using servo motor
"""
import time
import logging

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available, using mock barrier")

logger = logging.getLogger(__name__)


class BarrierControl:
    """Barrier/Gate controller using servo motor"""

    def __init__(self, servo_pin=22, open_angle=90, close_angle=0):
        """Initialize barrier control"""
        self.servo_pin = servo_pin
        self.open_angle = open_angle
        self.close_angle = close_angle

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.servo_pin, GPIO.OUT)

            # Initialize PWM (50Hz for servo)
            self.pwm = GPIO.PWM(self.servo_pin, 50)
            self.pwm.start(0)

            # Initial state: closed
            self.close()

            self.mock_mode = False
            logger.info(f"Barrier control initialized (Pin: {servo_pin})")
        else:
            self.mock_mode = True
            self.state = 'closed'
            logger.warning("Using mock barrier control")

    def _angle_to_duty_cycle(self, angle):
        """Convert angle to PWM duty cycle"""
        # Servo duty cycle: 2.5% (0 deg) to 12.5% (180 deg)
        duty_cycle = 2.5 + (angle / 180.0) * 10.0
        return duty_cycle

    def open(self):
        """Open barrier"""
        if self.mock_mode:
            self.state = 'open'
            logger.info("[Barrier] OPEN")
            return

        duty_cycle = self._angle_to_duty_cycle(self.open_angle)
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)  # Wait for servo to move
        self.pwm.ChangeDutyCycle(0)  # Stop sending signal
        logger.info("Barrier opened")

    def close(self):
        """Close barrier"""
        if self.mock_mode:
            self.state = 'closed'
            logger.info("[Barrier] CLOSED")
            return

        duty_cycle = self._angle_to_duty_cycle(self.close_angle)
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)  # Wait for servo to move
        self.pwm.ChangeDutyCycle(0)  # Stop sending signal
        logger.info("Barrier closed")

    def cleanup(self):
        """Cleanup GPIO"""
        if GPIO_AVAILABLE and not self.mock_mode:
            self.close()
            self.pwm.stop()
            GPIO.cleanup([self.servo_pin])
            logger.info("Barrier GPIO cleaned up")
