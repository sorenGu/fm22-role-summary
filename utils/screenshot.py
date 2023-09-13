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


def crop_from_config(config, row_i, attribute_number, screenshotter) -> Image.Image:
    row_start = config.rows_starts[row_i]
    top_start = config.top + attribute_number * (config.height + config.height_between)
    padding = 8
    return screenshotter.get_crop(
        [row_start,
         top_start - padding,
         row_start + config.width,
         top_start + config.height + padding
         ])
