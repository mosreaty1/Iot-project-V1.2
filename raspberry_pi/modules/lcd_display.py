"""
LCD Display Module (16x2 or 20x4 LCD)
Uses HD44780 controller via GPIO
"""
import time
import logging

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available, using mock LCD")

logger = logging.getLogger(__name__)


class LCDDisplay:
    """16x2 LCD Display with HD44780 controller"""

    # LCD Commands
    LCD_CLEAR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_DISPLAY_CONTROL = 0x08
    LCD_FUNCTION_SET = 0x20

    # Entry mode flags
    LCD_ENTRY_LEFT = 0x02
    LCD_ENTRY_SHIFT_DECREMENT = 0x00

    # Display control flags
    LCD_DISPLAY_ON = 0x04
    LCD_CURSOR_OFF = 0x00
    LCD_BLINK_OFF = 0x00

    # Function set flags
    LCD_4BIT_MODE = 0x00
    LCD_2_LINE = 0x08
    LCD_5x8_DOTS = 0x00

    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005

    def __init__(self, rs_pin=7, en_pin=8, d4_pin=25, d5_pin=24, d6_pin=23, d7_pin=18, cols=16, rows=2):
        """Initialize LCD display"""
        self.rs_pin = rs_pin
        self.en_pin = en_pin
        self.d4_pin = d4_pin
        self.d5_pin = d5_pin
        self.d6_pin = d6_pin
        self.d7_pin = d7_pin
        self.cols = cols
        self.rows = rows

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.rs_pin, GPIO.OUT)
            GPIO.setup(self.en_pin, GPIO.OUT)
            GPIO.setup(self.d4_pin, GPIO.OUT)
            GPIO.setup(self.d5_pin, GPIO.OUT)
            GPIO.setup(self.d6_pin, GPIO.OUT)
            GPIO.setup(self.d7_pin, GPIO.OUT)

            # Initialize display
            self._init_display()
            self.mock_mode = False
            logger.info(f"LCD display initialized ({cols}x{rows})")
        else:
            self.mock_mode = True
            logger.warning("Using mock LCD display")

    def _init_display(self):
        """Initialize LCD in 4-bit mode"""
        time.sleep(0.05)

        # Initialize in 4-bit mode
        self._write_4bits(0x03)
        time.sleep(0.005)
        self._write_4bits(0x03)
        time.sleep(0.005)
        self._write_4bits(0x03)
        time.sleep(0.001)
        self._write_4bits(0x02)

        # Function set: 4-bit mode, 2 lines, 5x8 font
        self._write_command(self.LCD_FUNCTION_SET | self.LCD_4BIT_MODE |
                           self.LCD_2_LINE | self.LCD_5x8_DOTS)

        # Display control: display on, cursor off, blink off
        self._write_command(self.LCD_DISPLAY_CONTROL | self.LCD_DISPLAY_ON |
                           self.LCD_CURSOR_OFF | self.LCD_BLINK_OFF)

        # Clear display
        self.clear()

        # Entry mode: left to right
        self._write_command(self.LCD_ENTRY_MODE | self.LCD_ENTRY_LEFT |
                           self.LCD_ENTRY_SHIFT_DECREMENT)

    def _write_4bits(self, bits):
        """Write 4 bits to LCD"""
        GPIO.output(self.d4_pin, (bits & 0x01) == 0x01)
        GPIO.output(self.d5_pin, (bits & 0x02) == 0x02)
        GPIO.output(self.d6_pin, (bits & 0x04) == 0x04)
        GPIO.output(self.d7_pin, (bits & 0x08) == 0x08)
        self._pulse_enable()

    def _pulse_enable(self):
        """Pulse the enable pin"""
        GPIO.output(self.en_pin, GPIO.LOW)
        time.sleep(self.E_DELAY)
        GPIO.output(self.en_pin, GPIO.HIGH)
        time.sleep(self.E_PULSE)
        GPIO.output(self.en_pin, GPIO.LOW)
        time.sleep(self.E_DELAY)

    def _write_byte(self, byte, mode):
        """Write byte to LCD in 4-bit mode"""
        GPIO.output(self.rs_pin, mode)

        # High nibble
        self._write_4bits(byte >> 4)
        # Low nibble
        self._write_4bits(byte & 0x0F)

    def _write_command(self, cmd):
        """Write command to LCD"""
        self._write_byte(cmd, GPIO.LOW)

    def _write_char(self, char):
        """Write character to LCD"""
        self._write_byte(ord(char), GPIO.HIGH)

    def clear(self):
        """Clear LCD display"""
        if self.mock_mode:
            logger.info("[LCD] Clear")
            return

        self._write_command(self.LCD_CLEAR)
        time.sleep(0.002)

    def set_cursor(self, col, row):
        """Set cursor position"""
        if self.mock_mode:
            return

        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row < len(row_offsets):
            self._write_command(0x80 | (col + row_offsets[row]))

    def write_string(self, text, col=0, row=0):
        """Write string to LCD at specified position"""
        if self.mock_mode:
            logger.info(f"[LCD Row {row}] {text}")
            return

        self.set_cursor(col, row)
        for char in text:
            self._write_char(char)

    def display_message(self, line1, line2=""):
        """Display message on LCD (line 1 and line 2)"""
        if self.mock_mode:
            logger.info(f"[LCD] Line 1: {line1}")
            if line2:
                logger.info(f"[LCD] Line 2: {line2}")
            return

        self.clear()
        # Truncate lines to fit display
        line1 = line1[:self.cols]
        line2 = line2[:self.cols]

        self.write_string(line1, 0, 0)
        if line2 and self.rows > 1:
            self.write_string(line2, 0, 1)

    def cleanup(self):
        """Cleanup LCD"""
        if not self.mock_mode:
            self.clear()
            logger.info("LCD cleaned up")
