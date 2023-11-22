import argparse
import json
import logging
from pprint import pprint
from typing import List, Dict, Optional, Iterator, TypedDict

from utils.console_display import color_display_attribute_value
from utils.data_gatherer import TeamData
from utils.role_config import POSITION_MAPPING, POSITION_MAPPING_GK, TeamConfig

parser = argparse.ArgumentParser(description='Process command-line arguments.')
parser.add_argument('-t', '--team', required=False, type=str, help='Key team to compare', default=None)
args: argparse.Namespace = parser.parse_args()


def find_best_constellation(keys: list, data: dict, chosen_ids: list, current_position: int = 0, total_value: int = 0,
                            depth: int = 5):
    if current_position == len(keys):
        return chosen_ids, total_value

    best_constellation = None
    max_value = float('-inf')
    i = 0
    for id_, value in data[keys[current_position]].items():
        if i > depth:
            break
        i += 1
        if id_ not in chosen_ids:
            new_chosen_ids = chosen_ids + [id_]
            new_total_value = total_value + value

            result = find_best_constellation(keys, data, new_chosen_ids, current_position + 1, new_total_value)

            if result and result[1] > max_value:
                max_value = result[1]
                best_constellation = result

    return best_constellation


def main(team: str, **kwargs):
    team_config = TeamConfig(team)
    team_data = TeamData(team_config)

    best_constellation = find_best_constellation(team_config.roles_in_team, team_data.original_data, [], depth=1)
    print(f"Value: {best_constellation[1]}")
    for position, player in zip(team_config.roles_in_team, best_constellation[0]):
        score = team_data.original_data[position][player]
        print(f"{position}: {player} {color_display_attribute_value(score)}")


if __name__ == "__main__":
    _team = args.team if args.team else "bromly_3421"
    main(_team)
