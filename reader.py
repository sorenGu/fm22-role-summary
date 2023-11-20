import argparse
import json
import logging
from typing import List, Dict, Optional, Iterator, TypedDict

from utils.data_gatherer import TeamData
from utils.role_config import POSITION_MAPPING, POSITION_MAPPING_GK, TeamConfig

parser = argparse.ArgumentParser(description='Process command-line arguments.')
parser.add_argument('-t', '--team', required=False, type=str, help='Key team to compare', default=None)
parser.add_argument('-s', '--save', action='store_true')
args: argparse.Namespace = parser.parse_args()


class AttributeMapping(TypedDict):
    player: Dict[str, int]
    gk: Dict[str, int]


class Attributes(TypedDict):
    player: List[Optional[int]]
    gk: List[Optional[int]]


class AttributeExtra(TypedDict):
    found: bool
    guessed: bool
    not_found: int


file_name = "players"
input_file = f"C:\\Users\\Soeren\\Documents\\Sports Interactive\\Football Manager 2024\\{file_name}.rtf"

logging.basicConfig(filename='data/reader_output.txt', level=logging.DEBUG, format='', encoding='utf-8')

def iterate_lines() -> Iterator[List[str]]:
    with open(input_file, "r", encoding="utf8") as f:
        for line in f.readlines():
            data = line.split("|")
            if len(data) < 4:
                continue

            yield data

"|Rec|Inf|Name|Age|Acc|Aer|Agg|Agi|Ant|Bal|Bra|Cmd|Com|Cmp|Cnt|Cor|Cro|Dec|Det|Dri|Ecc|Fin|Fir|Fla|Fre|Han|Hea|Jum|Kic|Ldr|Lon|L Th|Mar|Nat|OtB|1v1|Pac|Pas|Pen|Pos|Pun|Ref|TRO|Sta|Str|Tck|Tea|Tec|Thr|Vis|Wor|"


def get_player_attributes(data, header) -> tuple[Attributes, AttributeExtra]:
    attributes: Attributes = {
        "player": [None] * len(POSITION_MAPPING),
        "gk": [None] * len(POSITION_MAPPING_GK),
    }
    attributes_extra: AttributeExtra = {
        "found": False,
        "guessed": False,
        "not_found": 0
    }

    for attribute_name, attribute_value in zip(header, data):
        try:
            if "-" in attribute_value:
                attribute_value = attribute_value.split("-")
                int_value = (int(attribute_value[0]) + int(attribute_value[1])) / 2
                attributes_extra["guessed"] = True
            else:
                int_value = int(attribute_value)
            attributes_extra["found"] = True
        except ValueError:
            attributes_extra["not_found"] += 1
            continue

        for role_category, mapping in zip(attributes.keys(), (POSITION_MAPPING, POSITION_MAPPING_GK)):
            try:
                attribute_position = mapping.index(attribute_name)
            except ValueError:
                continue

            attributes[role_category][attribute_position] = int_value

    return attributes, attributes_extra


def main(team: str, save, **kwargs):
    team_config = TeamConfig(team)
    team_data = TeamData(team_config)
    team_data.set_comparison_values()

    gather_data(team_data)

    team_data.display_all_roles()

    if save:
        team_data.save_data_to_file("data/reader_output.json")


def gather_data(team_data):
    attribute_mapping_is_set = False
    header = []
    for data in iterate_lines():
        age = data[4].strip()
        name = data[3].strip().split(" ")
        name = f"{name[0][:3]} {name[-1]} {age}"
        positions = data[5].strip().lower()
        data = data[6:-1]

        if not attribute_mapping_is_set:
            header = [x.strip() for x in data]
            attribute_mapping_is_set = True
            continue

        attributes, attributes_extra = get_player_attributes(data, header)
        attributes: Attributes
        attributes_extra: AttributeExtra

        if not attributes_extra["found"]:
            continue

        if attributes_extra["not_found"]:
            name += "**"
            if attributes_extra["not_found"] > 5:
                continue
            try:
                attributes = {key: replace_nones_with_average(value) for key, value in attributes.items()}
            except ZeroDivisionError:
                continue
        elif attributes_extra["guessed"]:
            name += "*"

        for role_category, _attributes in attributes.items():
            if attributes_extra["not_found"] and (role_category == "gk") != ("gk" in positions):
                continue
            team_data.add_player_to_team(name, _attributes)


def set_headers(attribute_mapping: AttributeMapping, header_row: List[str]):
    for i, header in enumerate(header_row):
        if header in POSITION_MAPPING:
            attribute_mapping["player"][header] = i
        if header in POSITION_MAPPING_GK:
            attribute_mapping["gk"][header] = i


def replace_nones_with_average(attributes: List[Optional[int]]) -> List[int]:
    filtered_attributes = list(filter(None, attributes))
    average = .8 * sum(filtered_attributes) / len(filtered_attributes)
    return [x if x is not None else average for x in attributes]


if __name__ == "__main__":
    team = args.team if args.team else "hsv_gold"
    main(team, args.save)
