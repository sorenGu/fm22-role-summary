import json
import sys
from json import JSONDecodeError
from typing import Union

from PIL import Image

from utils.config import elements_per_row

ROLE_DATA_FILE = "role_data.json"
COLORS = {
    "key": (55, 68, 58),
    "preferable": (50, 65, 80),
}


def is_pixel_close(pixel: tuple[int, int, int], target_color: tuple[int, int, int], tolerance: int = 10) -> bool:
    r1, g1, b1 = pixel
    r2, g2, b2 = target_color

    color_distance = ((r1 - r2) ** 2) + ((g1 - g2) ** 2) + ((b1 - b2) ** 2)
    return color_distance <= tolerance ** 2


def match_color(image: Image.Image) -> Union[None, str]:
    image_pixel = image.getpixel((1, 7))
    for key, color in COLORS.items():
        if is_pixel_close(color, image_pixel):
            return key


class RoleConfig:
    def read_config(self):
        with open(ROLE_DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except JSONDecodeError as e:
                print(f"failed to read config {e}")
                return {}

    def get_importance(self, image, row_i, attribute_number):
        pass

    def end(self):
        pass



class ColorParserRoleConfig(RoleConfig):
    def get_importance(self, image, row_i, attribute_number):
        return match_color(image)


IMPORTANCE_STR = Union[None, str]


class SaveRoleConfig(ColorParserRoleConfig):
    def __init__(self, role_name: str):
        role_data = self.read_config()
        if role_name in role_data:
            answer = input(f"Do you want to override {role_name}? (y/n)")
            if answer != "y":
                sys.exit()

        self.role_name = role_name
        self.role_config: tuple[list[IMPORTANCE_STR], list[IMPORTANCE_STR], list[IMPORTANCE_STR]] = tuple(
            [None for _ in range(row_element_number)] for
            row_element_number in elements_per_row
        )

    def get_importance(self, image, row_i, attribute_number):
        importance = super().get_importance(image, row_i, attribute_number)
        self.role_config[row_i][attribute_number] = importance
        return importance

    def end(self):
        role_data = self.read_config()
        role_data[self.role_name] = self.role_config

        with open(ROLE_DATA_FILE, "w") as f:
            json.dump(role_data, f)


class UseRoleConfig(RoleConfig):
    def __init__(self, role_name: str):
        role_data = self.read_config()
        try:
            self.role_config = role_data[role_name]
        except KeyError:
            print(f"Failed to find role {role_name}. Available roles: {role_data.keys()}")
            sys.exit()

    def get_importance(self, image, row_i, attribute_number):
        return self.role_config[row_i][attribute_number]
