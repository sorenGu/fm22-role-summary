import json
import sys
from json import JSONDecodeError
from typing import Union, Dict, TypedDict, List, cast, Optional, TypeAlias, Type, Literal

from PIL import Image

from utils.config import DefaultConfig



def is_pixel_close(pixel: tuple[int, int, int], target_color: tuple[int, int, int], tolerance: int = 20) -> bool:
    r1, g1, b1 = pixel
    r2, g2, b2 = target_color

    color_distance = ((r1 - r2) ** 2) + ((g1 - g2) ** 2) + ((b1 - b2) ** 2)
    return color_distance <= tolerance ** 2

def get_relevant_pixel(image: Image.Image):
    return image.getpixel((1, 7))

"""
|Rec|Inf|Name|Age|Acc|Aer|Agg|Agi|Ant|Bal|Bra|Cmd|Com|Cmp|Cnt|Cor|Cro|Dec|Det|Dri|Ecc|Fin|Fir|Fla|Fre|Han|Hea|Jum|Kic|Ldr|Lon|L Th|Mar|Nat|OtB|1v1|Pac|Pas|Pen|Pos|Pun|Ref|TRO|Sta|Str|Tck|Tea|Tec|Thr|Vis|Wor|
"""

POSITION_MAPPING = (
    "Cor", "Cro", "Dri", "Fin", "Fir", "Fre", "Hea", "Lon", "L Th", "Mar", "Pas", "Pen", "Tck", "Tec",
    "Agg", "Ant", "Bra", "Cmp", "Cnt", "Dec", "Det", "Fla", "Ldr", "OtB", "Pos", "Tea", "Vis", "Wor",
    "Acc", "Agi", "Bal", "Jum", "Nat", "Pac", "Sta", "Str"
)

POSITION_MAPPING_GK = (
    "Aer", "Cmd", "Com", "Ecc", "Fir", "Han", "Kic", "1v1", "Pas", "Pun", "Ref", "TRO", "Thr",
    "Agg", "Ant", "Bra", "Cmp", "Cnt", "Dec", "Det", "Fla", "Ldr", "OtB", "Pos", "Tea", "Vis", "Wor",
    "Acc", "Agi", "Bal", "Jum", "Nat", "Pac", "Sta", "Str"
)


IMPORTANCE_STR: TypeAlias = Literal[None, "key", "preferable"]
ROLE_CONFIG: TypeAlias = List[IMPORTANCE_STR]
TeamConfigs: TypeAlias = Dict[str, List[str]]


class ConfigData(TypedDict):
    roles: Dict[str, ROLE_CONFIG]


class RoleConfigCache:
    FULL_DATA: ConfigData = None
    FILE = "data/role_config.json"

    @classmethod
    def save_config(cls, config):
        cls.FULL_DATA = config
        with open(RoleConfigCache.FILE, "w") as f:
            json.dump(config, f)

    @classmethod
    def read_config(cls) -> ConfigData:
        if cls.FULL_DATA is None:
            try:
                with open(cls.FILE, "r") as f:
                    data: ConfigData = json.load(f)
            except (JSONDecodeError, FileNotFoundError) as e:
                print(f"failed to read config {e}")
                data: ConfigData = {"roles": {}}

            cls.FULL_DATA = data

        return cls.FULL_DATA


def sort_role_data(key):
    position = key[0].split("_")[0].lower()
    position_order = ["gk", "dc", "dw", "dmc", "dmw", "mc", "mw", "amc", "amw", "st"]
    if position in position_order:
        return position_order.index(position)
    else:
        return 50


class ColorRoleGetter:
    def __init__(self, image_config: Type[DefaultConfig]):
        self.config: Type[DefaultConfig] = image_config

    def get_importance(self, image: Image.Image) -> Union[None, str]:
        image_pixel = get_relevant_pixel(image)
        for key, color in self.config.role_relevance_colors.items():
            if is_pixel_close(color, image_pixel):
                return key


class SaveRoleConfig(ColorRoleGetter):
    def __init__(self, role_name: str, image_config: Type[DefaultConfig], force=False):
        self.complete_config = RoleConfigCache.read_config()
        role_data = self.complete_config["roles"]
        if force is False and role_name in role_data:
            answer = input(f"Do you want to override {role_name}? (y/n)")
            if answer != "y":
                sys.exit()

        self.role_name = role_name
        super().__init__(image_config)

    def save_role_config(self, config: ROLE_CONFIG):
        role_data = self.complete_config["roles"]
        role_data[self.role_name] = config
        role_data = dict(sorted(role_data.items(), key=sort_role_data))

        self.complete_config["roles"] = role_data

        RoleConfigCache.save_config(self.complete_config)


class TeamConfig:
    FILE = "data/team_config.json"
    def __init__(self, team_name):
        self.name = team_name
        config = RoleConfigCache.read_config()
        self.role_configs = config["roles"]
        try:
            self.roles_in_team = self.read_config()[team_name]
        except KeyError:
            raise ValueError(f"Team {team_name} not found in config file: {RoleConfigCache.FILE}")

    @classmethod
    def read_config(cls) -> TeamConfigs:
        try:
            with open(cls.FILE, "r") as f:
                config: TeamConfigs = json.load(f)["teams"]
        except (JSONDecodeError, FileNotFoundError) as e:
            print(f"failed to read config {e}")
            config: TeamConfigs = {}
        return config
