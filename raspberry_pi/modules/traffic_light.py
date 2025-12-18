"""
Traffic Light Module (Red/Green LEDs)
Controls access indication lights
"""
import logging

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available, using mock traffic light")

logger = logging.getLogger(__name__)


class TrafficLight:
    """Traffic light controller (Red and Green LEDs)"""

    def __init__(self, red_pin=17, green_pin=27):
        """Initialize traffic light"""
        self.red_pin = red_pin
        self.green_pin = green_pin

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.red_pin, GPIO.OUT)
            GPIO.setup(self.green_pin, GPIO.OUT)

            # Initial state: red light on
            GPIO.output(self.red_pin, GPIO.HIGH)
            GPIO.output(self.green_pin, GPIO.LOW)

            self.mock_mode = False
            logger.info(f"Traffic light initialized (Red: {red_pin}, Green: {green_pin})")
        else:
            self.mock_mode = True
            self.state = 'red'
            logger.warning("Using mock traffic light")

    def red(self):
        """Turn on red light, turn off green"""
        if self.mock_mode:
            self.state = 'red'
            logger.info("[Traffic Light] RED")
            return

        GPIO.output(self.red_pin, GPIO.HIGH)
        GPIO.output(self.green_pin, GPIO.LOW)
        logger.debug("Traffic light: RED")

    def green(self):
        """Turn on green light, turn off red"""
        if self.mock_mode:
            self.state = 'green'
            logger.info("[Traffic Light] GREEN")
            return

        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.HIGH)
        logger.debug("Traffic light: GREEN")

    def off(self):
        """Turn off both lights"""
        if self.mock_mode:
            self.state = 'off'
            logger.info("[Traffic Light] OFF")
            return

        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.LOW)
        logger.debug("Traffic light: OFF")

    def cleanup(self):
        """Cleanup GPIO"""
        if GPIO_AVAILABLE and not self.mock_mode:
            self.off()
            GPIO.cleanup([self.red_pin, self.green_pin])
            logger.info("Traffic light GPIO cleaned up")
