import json
import sys
from json import JSONDecodeError
from typing import Union, Dict

from PIL import Image

from utils.config import elements_per_row, DefaultConfig


COLORS = DefaultConfig.role_relevance_colors


def is_pixel_close(pixel: tuple[int, int, int], target_color: tuple[int, int, int], tolerance: int = 20) -> bool:
    r1, g1, b1 = pixel
    r2, g2, b2 = target_color

    color_distance = ((r1 - r2) ** 2) + ((g1 - g2) ** 2) + ((b1 - b2) ** 2)
    return color_distance <= tolerance ** 2


def match_color(image: Image.Image) -> Union[None, str]:
    image_pixel = get_relevant_pixel(image)
    for key, color in COLORS.items():
        if is_pixel_close(color, image_pixel):
            return key


def get_relevant_pixel(image: Image.Image):
    return image.getpixel((1, 7))


class RoleConfigCache:
    FULL_DATA = None
    CURRENT_TEAM = "default"
    FILE = "role_data.json"

    @classmethod
    def set_team(cls, team):
        cls.CURRENT_TEAM = team


class RoleConfig:
    @staticmethod
    def read_config() -> Dict:
        if RoleConfigCache.FULL_DATA is None:
            try:
                with open(RoleConfigCache.FILE, "r") as f:
                    data = json.load(f)
            except (JSONDecodeError, FileNotFoundError) as e:
                print(f"failed to read config {e}")
                data = {}

            RoleConfigCache.FULL_DATA = data

        return RoleConfigCache.FULL_DATA.get(RoleConfigCache.CURRENT_TEAM, {})


    def get_importance(self, image, row_i, attribute_number):
        pass

    def end(self):
        pass

    @staticmethod
    def save_data(role_data):
        RoleConfigCache.FULL_DATA[RoleConfigCache.CURRENT_TEAM] = role_data
        with open(RoleConfigCache.FILE, "w") as f:
            json.dump(RoleConfigCache.FULL_DATA, f)


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
        RoleConfig.save_data(role_data)


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
