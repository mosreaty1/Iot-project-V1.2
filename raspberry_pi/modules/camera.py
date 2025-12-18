"""
Camera Module for License Plate Recognition
Uses PiCamera and EasyOCR/Tesseract for plate recognition
"""
import os
from datetime import datetime
import logging

try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    logging.warning("Picamera2 not available, using mock camera")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logging.warning("EasyOCR not available")

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("Tesseract not available")

import cv2
import re

logger = logging.getLogger(__name__)


class CameraModule:
    """Camera module for capturing and processing vehicle images"""

    def __init__(self, image_dir='/tmp/vehicle_images'):
        """Initialize camera module"""
        self.image_dir = image_dir
        os.makedirs(image_dir, exist_ok=True)

        # Initialize camera
        if PICAMERA_AVAILABLE:
            try:
                self.camera = Picamera2()
                config = self.camera.create_still_configuration()
                self.camera.configure(config)
                self.camera.start()
                self.camera_type = 'picamera'
                logger.info("PiCamera2 initialized")
            except Exception as e:
                logger.error(f"Failed to initialize PiCamera2: {e}")
                self.camera = None
                self.camera_type = 'mock'
        else:
            self.camera = None
            self.camera_type = 'mock'

        # Initialize OCR
        if EASYOCR_AVAILABLE:
            self.reader = easyocr.Reader(['en'], gpu=False)
            self.ocr_type = 'easyocr'
            logger.info("EasyOCR initialized")
        elif TESSERACT_AVAILABLE:
            self.ocr_type = 'tesseract'
            logger.info("Tesseract initialized")
        else:
            self.ocr_type = 'mock'
            logger.warning("No OCR available, using mock recognition")

    def capture_image(self):
        """Capture image from camera"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = os.path.join(self.image_dir, f'vehicle_{timestamp}.jpg')

        try:
            if self.camera_type == 'picamera' and self.camera:
                self.camera.capture_file(image_path)
                logger.info(f"Image captured: {image_path}")
                return image_path
            elif self.camera_type == 'mock':
                # Mock capture for testing
                logger.warning("Using mock camera capture")
                return self._create_mock_image(image_path)
        except Exception as e:
            logger.error(f"Failed to capture image: {e}")
            return None

    def _create_mock_image(self, image_path):
        """Create a mock image for testing"""
        import numpy as np
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(mock_image, 'ABC-1234', (200, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        cv2.imwrite(image_path, mock_image)
        return image_path

    def recognize_plate(self, image_path):
        """Recognize license plate from image"""
        try:
            if self.ocr_type == 'easyocr':
                return self._recognize_with_easyocr(image_path)
            elif self.ocr_type == 'tesseract':
                return self._recognize_with_tesseract(image_path)
            else:
                return self._mock_recognition(image_path)
        except Exception as e:
            logger.error(f"Plate recognition error: {e}")
            return None

    def _recognize_with_easyocr(self, image_path):
        """Recognize plate using EasyOCR"""
        result = self.reader.readtext(image_path)

        for detection in result:
            text = detection[1].upper()
            # Clean and validate plate number
            plate = self._clean_plate_text(text)
            if self._validate_plate(plate):
                logger.info(f"Plate recognized: {plate}")
                return plate

        logger.warning("No valid plate found in image")
        return None

    def _recognize_with_tesseract(self, image_path):
        """Recognize plate using Tesseract"""
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, config='--psm 7')
        plate = self._clean_plate_text(text)

        if self._validate_plate(plate):
            logger.info(f"Plate recognized: {plate}")
            return plate

        logger.warning("No valid plate found in image")
        return None

    def _mock_recognition(self, image_path):
        """Mock recognition for testing"""
        logger.warning("Using mock plate recognition")
        return "ABC1234"

    def _clean_plate_text(self, text):
        """Clean and format plate text"""
        # Remove special characters except letters and numbers
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        return cleaned

    def _validate_plate(self, plate):
        """Validate plate number format"""
        # Basic validation: should contain both letters and numbers
        if len(plate) < 3:
            return False
        has_letter = any(c.isalpha() for c in plate)
        has_number = any(c.isdigit() for c in plate)
        return has_letter and has_number

    def cleanup(self):
        """Cleanup camera resources"""
        if self.camera_type == 'picamera' and self.camera:
            try:
                self.camera.stop()
                logger.info("Camera stopped")
            except Exception as e:
                logger.error(f"Error stopping camera: {e}")
