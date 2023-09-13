import sys

import cv2
import numpy as np
from PIL import Image
from pytesseract import pytesseract


class FailedToParseNumber(Exception):
    pass


def image_to_int(screenshot=Image.Image):
    screenshot = screenshot.resize((int(3 * s) for s in screenshot.size))
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Convert image to grayscale
    gray_img = cv2.cvtColor(screenshot_cv, cv2.COLOR_RGB2GRAY)

    # Thresholding
    _, threshold_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_OTSU)

    # Invert colors
    inverted_img = cv2.bitwise_not(threshold_img)

    # Convert OpenCV image back to PIL format
    inverted_pil = Image.fromarray(inverted_img)
    # inverted_pil = inverted_pil.resize((int(3 * s) for s in inverted_pil.size))

    try:
        return int(pytesseract.image_to_string(inverted_pil).replace("\n", "").split("-")[-1])
    except Exception:
        return int(pytesseract.image_to_string(inverted_pil, config='--psm 10').replace("\n", "").split("-")[-1])


