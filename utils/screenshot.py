from typing import Type, Generator, Tuple, TypeAlias, Iterator, List
from warnings import warn

import pyautogui
from PIL import Image

from utils.config import DefaultConfig
from utils.image_to_text import image_to_str, image_to_int

Rect: TypeAlias = list[int, int, int, int]


class Screenshotter:
    screenshot = None
    black_white_threshold = 150

    def __init__(self):
        self.reset_screenshot()

    def reset_screenshot(self):
        self.screenshot = pyautogui.screenshot()

    def get_crop(self, rect: Rect, relative: bool = False) -> Image.Image:

        if relative is True:
            rect[2] += rect[0]
            rect[3] += rect[1]

        cropped_image = self.screenshot.crop(rect)

        return cropped_image


class ConfiguredScreenshotter(Screenshotter):
    def __init__(self, screen_reader_config):
        super().__init__()
        self.config: Type[DefaultConfig] = screen_reader_config

    def _iterate_attribute_positions(self, rows_per_column: Tuple[int, int, int] = (14, 14, 8)) -> Iterator[Rect]:
        for column in range(3):
            row_start = self.config.rows_starts[column]
            for row in range(rows_per_column[column]):
                top_start = self.config.top + row * (self.config.height + self.config.height_between)
                yield [row_start,
                       top_start - self.config.padding,
                       row_start + self.config.width,
                       top_start + self.config.height + self.config.padding
                       ]

    def iterate_attribute_images(self, is_goalkeeper=False) -> Iterator[Image.Image]:
        if is_goalkeeper:
            rows_per_column = (13, 14, 8)
        else:
            rows_per_column = (14, 14, 8)

        for rect in self._iterate_attribute_positions(rows_per_column):
            yield self.get_crop(rect)

    def _get_name_rect(self) -> Rect:
        return [self.config.name_x,
                self.config.name_y,
                self.config.name_x + self.config.name_width,
                self.config.name_y + self.config.name_height
        ]

    def get_name_image(self) -> Image.Image:
        return self.get_crop(self._get_name_rect())

def crop_name_from_config(config, screenshotter) -> Image.Image:
    warn('This is deprecated', DeprecationWarning, stacklevel=2)
    return screenshotter.get_crop(
        )


def crop_from_config(config, row_i, attribute_number, screenshotter) -> Image.Image:
    warn('This is deprecated', DeprecationWarning, stacklevel=2)
    row_start = config.rows_starts[row_i]
    top_start = config.top + attribute_number * (config.height + config.height_between)

    return screenshotter.get_crop(
        [row_start,
         top_start - config.padding,
         row_start + config.width,
         top_start + config.height + config.padding
         ])


def get_player_name(screenshotter):
    return image_to_str(
        screenshotter.get_name_image(),
        config="-c tessedit_char_blacklist=.\\\”:\\\"-,").split(" ")[-1].capitalize()


def gather_attributes(screenshotter) -> List[int]:
    attributes: List[int] = []
    for i, attribute_image in enumerate(screenshotter.iterate_attribute_images()):
        try:
            value = image_to_int(attribute_image)
        except ValueError:
            value = None

        if i == 13:  # attribute that is empty for gk's
            if value is None:
                continue
            if value == 4 and input("Is this a goalkeeper? (y/n)") == "y":
                continue
        if value is None:
            attribute_image.show()
            raise ValueError("Failed to parse image to int")

        attributes.append(value)
    return attributes
