import json
import sys
from json import JSONDecodeError
from typing import Union, Dict, TypedDict, List, cast

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

"""
|Rec|Inf|Name|Age|Acc|Aer|Agg|Agi|Ant|Bal|Bra|Cmd|Com|Cmp|Cnt|Cor|Cro|Dec|Det|Dri|Ecc|Fin|Fir|Fla|Fre|Han|Hea|Jum|Kic|Ldr|Lon|L Th|Mar|Nat|OtB|1v1|Pac|Pas|Pen|Pos|Pun|Ref|TRO|Sta|Str|Tck|Tea|Tec|Thr|Vis|Wor|
"""

POSITION_MAPPING = (
    ("Cor", "Cro", "Dri", "Fin", "Fir", "Fre", "Hea", "Lon", "L Th", "Mar", "Pas", "Pen", "Tck", "Tec"),
    ("Agg", "Ant", "Bra", "Cmp", "Cnt", "Dec", "Det", "Fla", "Ldr", "OtB", "Pos", "Tea", "Vis", "Wor"),
    ("Acc", "Agi", "Bal", "Jum", "Nat", "Pac", "Sta", "Str")
)

POSITION_MAPPING_GK = (
    ("Aer", "Cmd", "Com", "Ecc", "Fir", "Han", "Kic", "1v1", "Pas", "Pun", "Ref", "TRO", "Thr"),
    ("Agg", "Ant", "Bra", "Cmp", "Cnt", "Dec", "Det", "Fla", "Ldr", "OtB", "Pos", "Tea", "Vis", "Wor"),
    ("Acc", "Agi", "Bal", "Jum", "Nat", "Pac", "Sta", "Str")
)


IMPORTANCE_STR = Union[None, str]
ROLE_CONFIG_TYPE = tuple[list[IMPORTANCE_STR], list[IMPORTANCE_STR], list[IMPORTANCE_STR]]


class ConfigData(TypedDict):
    roles: Dict[str, ROLE_CONFIG_TYPE]
    teams: Dict[str, List[str]]


class RoleConfigCache:
    FULL_DATA: ConfigData = None
    CURRENT_TEAM = "default"
    FILE = "data/role_config.json"

    @classmethod
    def set_team(cls, team):
        cls.CURRENT_TEAM = team


class RoleConfig:
    @staticmethod
    def read_config() -> ConfigData:
        if RoleConfigCache.FULL_DATA is None:
            try:
                with open(RoleConfigCache.FILE, "r") as f:
                    data: ConfigData = json.load(f)
            except (JSONDecodeError, FileNotFoundError) as e:
                print(f"failed to read config {e}")
                data: ConfigData = {"roles": {}, "teams": {}}

            RoleConfigCache.FULL_DATA = data

        return RoleConfigCache.FULL_DATA

    def get_importance(self, image, row_i, attribute_number):
        pass

    def end(self):
        pass

    @staticmethod
    def save_data(role_data):
        RoleConfigCache.FULL_DATA["roles"] = role_data
        with open(RoleConfigCache.FILE, "w") as f:
            json.dump(RoleConfigCache.FULL_DATA, f)


class ColorParserRoleConfig(RoleConfig):
    def get_importance(self, image, row_i, attribute_number):
        return match_color(image)


def sort_role_data(key):
    position = key[0].split("_")[0].lower()
    position_order = ["gk", "dc", "dw", "dmc", "dmw", "mc", "mw", "amc", "amw", "st"]
    if position in position_order:
        return position_order.index(position)
    else:
        return 50

class SaveRoleConfig(ColorParserRoleConfig):
    def __init__(self, role_name: str):
        role_data = self.read_config()["roles"]
        if role_name in role_data:
            answer = input(f"Do you want to override {role_name}? (y/n)")
            if answer != "y":
                sys.exit()

        self.role_name = role_name

        self.role_config: ROLE_CONFIG_TYPE = tuple(
            [None for _ in range(row_element_number)] for
            row_element_number in elements_per_row
        )

    def get_importance(self, image, row_i, attribute_number):
        importance = super().get_importance(image, row_i, attribute_number)
        self.role_config[row_i][attribute_number] = importance
        return importance

    def end(self):
        role_data = self.read_config()["roles"]
        role_data[self.role_name] = self.role_config
        role_data = dict(sorted(role_data.items(), key=sort_role_data))
        RoleConfig.save_data(role_data)
