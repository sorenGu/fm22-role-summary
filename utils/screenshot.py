from typing import Union

import pyautogui
from PIL import Image


class Screenshotter:
    screenshot = None
    black_white_threshold = 150

    def __init__(self):
        self.reset_screenshot()

    def reset_screenshot(self):
        self.screenshot = pyautogui.screenshot()

    def get_crop(self, rect: list[int, int, int, int], relative: bool = False) -> Image.Image:

        if relative is True:
            rect[2] += rect[0]
            rect[3] += rect[1]

        cropped_image = self.screenshot.crop(rect)

        return cropped_image

