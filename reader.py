import argparse
import json
import logging
from colorama import init as colorama_init, Style
from collections import defaultdict
from typing import List, Dict, Tuple

from utils.gatherer import RoleGatherer
from utils.role_config import RoleConfig, POSITION_MAPPING, RoleConfigCache, POSITION_MAPPING_GK
from utils.team_gatherer import TeamData
from utils.util import HighScoreTracker, display_name

parser = argparse.ArgumentParser(description='Process command-line arguments.')
parser.add_argument('-t', '--team', required=False, type=str, help='Key team to compare', default=None)
parser.add_argument('-s', '--save', action='store_true')
args: argparse.Namespace = parser.parse_args()


class Found(Exception):
    pass


class InvalidPlayer(Exception):
    pass


class NotFound(Exception):
    def __init__(self, attribute_name):
        super().__init__()
        print(f"not found {attribute_name}")
        self.attribute_name = attribute_name


file_name = "players"
input_file = f"C:\\Users\\Soeren\\Documents\\Sports Interactive\\Football Manager 2024\\{file_name}.rtf"

logging.basicConfig(filename='data/reader_output.txt', level=logging.DEBUG, format='', encoding='utf-8')


"|Rec|Inf|Name|Age|Acc|Aer|Agg|Agi|Ant|Bal|Bra|Cmd|Com|Cmp|Cnt|Cor|Cro|Dec|Det|Dri|Ecc|Fin|Fir|Fla|Fre|Han|Hea|Jum|Kic|Ldr|Lon|L Th|Mar|Nat|OtB|1v1|Pac|Pas|Pen|Pos|Pun|Ref|TRO|Sta|Str|Tck|Tea|Tec|Thr|Vis|Wor|"
def main(team: str, save, **kwargs):
    role_config: RoleConfig = RoleConfig()

    RoleConfigCache.set_team(team)
    gatherers: List[RoleGatherer] = []
    config = role_config.read_config()

    team_data = TeamData.read_config().get(team, {})

    for role_name in config["teams"][team]:
        gatherer = RoleGatherer(role_name, config["roles"][role_name])
        gatherer.highscore = HighScoreTracker()
        try:
            gatherer.highscore.comparison_value = list(team_data.get(role_name, {}).values())[0]
        except IndexError:
            pass
        gatherers.append(gatherer)

    attribute_order_is_set = False
    attribute_order: Dict[int, Tuple[int, int]] = {}
    attribute_gk_order: Dict[int, Tuple[int, int]] = {}

    attributes = ([], [], [])
    attributes_gk = ([], [], [])
    for i, row in enumerate(POSITION_MAPPING):
        for _ in row:
            attributes[i].append(None)

    for i, row in enumerate(POSITION_MAPPING):
        for _ in row:
            attributes_gk[i].append(None)

    with open(input_file, "r", encoding="utf8") as f:
        for line in f.readlines():
            data = line.split("|")
            if len(data) < 4:
                continue

            name = data[3].strip()
            age = data[4].strip()
            data = data[5:-1]

            if not attribute_order_is_set:
                for header_i, header in enumerate(data):
                    header = header.strip()
                    try:
                        for x, row in enumerate(POSITION_MAPPING):
                            for y, attribute_name in enumerate(row):
                                if attribute_name == header:
                                    attribute_order[header_i] = (x, y)
                                    raise Found
                    except Found:
                        continue

                for header_i, header in enumerate(data):
                    header = header.strip()
                    try:
                        for x, row in enumerate(POSITION_MAPPING_GK):
                            for y, attribute_name in enumerate(row):
                                if attribute_name == header:
                                    attribute_gk_order[header_i] = (x, y)
                                    raise Found
                    except Found:
                        continue
                attribute_order_is_set = True
                continue

            try:
                for i, attribute_value in enumerate(data):

                    position = attribute_order.get(i)
                    gk_position = attribute_gk_order.get(i)
                    if position is None and gk_position is None:
                        continue

                    try:
                        if "-" in attribute_value:
                            attribute_value = attribute_value.split("-")
                            attribute_value = (int(attribute_value[0]) + int(attribute_value[1])) / 2
                            if not name.endswith("*"):
                                name += "*"
                        else:
                            attribute_value = int(attribute_value)
                    except ValueError:
                        raise InvalidPlayer

                    if position:
                        attributes[position[0]][position[1]] = attribute_value
                    if gk_position:
                        attributes_gk[gk_position[0]][gk_position[1]] = attribute_value

            except InvalidPlayer:
                continue
            max_score = -10000000
            for gatherer in gatherers:
                gatherer.reset()

                is_goalkeeper_attributes = gatherer.role_name.startswith("GK")
                attributes_for_gatherer = attributes if not is_goalkeeper_attributes else attributes_gk

                for row_i, row in enumerate(attributes_for_gatherer):
                    for attribute_number, value in enumerate(row):
                        if is_goalkeeper_attributes and value is None and row_i == 0 and attribute_number == 13:
                            continue
                        gatherer.add_to_row(row_i, attribute_number, value)
                gatherer.compile_complete_data()
                if gatherer.complete_data.average_value > max_score:
                    max_score = gatherer.complete_data.average_value

            for gatherer in gatherers:
                if gatherer.complete_data.average_value / max_score < .97:
                    continue
                gatherer.highscore.try_add_score(f"{name} ({age})", gatherer.complete_data.average_value_repr)

    logging.info(f"\n-------------------{team}----------------------------")
    for gatherer in gatherers:
        logging.info(gatherer.highscore.output(gatherer.role_name, display_name))
        print(Style.RESET_ALL + gatherer.highscore.output(gatherer.role_name)[:280] + Style.RESET_ALL)

    if save:
        output = {}
        for gatherer in gatherers:
            output[gatherer.role_name] = {}
            for name, value in gatherer.highscore._highscores.items():
                name = name.split(" ")[-2]
                output[gatherer.role_name][name] = value
        with open("data/reader_output.json", "w") as f:
            json.dump(output, f)


if __name__ == "__main__":
    colorama_init()

    team = args.team if args.team else "hsv_gyr"

    main(team, args.save)
