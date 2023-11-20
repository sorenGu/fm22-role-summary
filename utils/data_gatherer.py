import json
from json import JSONDecodeError
from typing import List, Dict

from utils.console_display import display_tracker, display_normalized_attributes, display_role_values
from utils.role_config import ROLE_CONFIG, IMPORTANCE_STR, TeamConfig, RoleConfigCache
from utils.util import HighScoreTracker


def calc_average(role_config: ROLE_CONFIG, attributes: List[int]):
    attribute_map: Dict[IMPORTANCE_STR, int] = {None: 1, "key": 10, "preferable": 5}
    weights = [attribute_map[attribute] for attribute in role_config]

    total_weight = sum(weights)

    if total_weight == 0:
        raise ValueError("Total weight cannot be zero.")

    weighted_sum = sum(value * weight for value, weight in zip(attributes, weights))

    return weighted_sum / total_weight


def normalize_value(value):
    return value * 10 - 100


class TeamData:
    CONFIG_FILE = "data/team_data.json"

    def __init__(self, team_config: TeamConfig):
        self.full_data = self.read_data()
        self.original_data = self.full_data.get(team_config.name, {})

        self.team_config = team_config
        self.data: Dict[str, HighScoreTracker] = {}
        self.init_data()

    def init_data(self):
        for role_name in self.team_config.roles_in_team:
            self.data[role_name] = HighScoreTracker(score_quantity=20)

    @classmethod
    def read_data(cls):
        try:
            with open(cls.CONFIG_FILE, "r") as f:
                return json.load(f)
        except (JSONDecodeError, FileNotFoundError) as e:
            return {}

    def set_comparison_values(self):
        for role_name, tracker in self.data.items():
            try:
                tracker.comparison_value = list(self.original_data.get(role_name, {}).values())[0]
            except IndexError:
                continue

    def display_all_roles(self, colored=True, highlighted_name=None):
        for role_name, tracker in self.data.items():
            print(display_tracker(tracker, role_name, colored, highlighted_name))

    def add_player_to_team(self, player_name, attributes, print_data=False, max_roles=3):
        attribute_count = len(attributes)
        if attribute_count == 35:
            is_goalkeeper = True
        elif attribute_count == 36:
            is_goalkeeper = False
        else:
            print(f"Failed to get correct count of attributes: {attribute_count}, expected 35 (goalkeeper) or 36")
            return

        all_attribute_average = sum(attributes) / len(attributes)
        max_value = -1

        if print_data:
            print(f"Player: {player_name} | average: {display_normalized_attributes(normalize_value(all_attribute_average))}")

        player_tracker = HighScoreTracker(score_quantity=500)
        for role_name, tracker in self.data.items():
            if is_goalkeeper != role_name.lower().startswith("gk"):
                continue

            try:
                role_config = self.team_config.role_configs[role_name]
            except KeyError:
                print(
                    f"Role {role_name} in Team {self.team_config.name} but not in roles in File: {RoleConfigCache.FILE}")
                return

            average = calc_average(role_config, attributes)
            player_tracker.try_add_score(role_name, average)
            if average > max_value:
                max_value = average


        for role_name, value in list(player_tracker.highscores.items())[:max_roles]:
            normalized = normalize_value(value)
            if print_data:
                print(display_role_values(role_name, normalized, (value / all_attribute_average) * 100, (value / max_value) * 100))
            self.data[role_name].try_add_score(player_name, normalized)

    def save_data_to_file(self, file_path):
        output = {}
        for role_name, tracker in self.data.items():
            output[role_name] = {name.split(" ")[1]: value for name, value in tracker.serialize().items()}
        with open(file_path, "w") as f:
            json.dump(output, f)


class TeamDataWithTeam(TeamData):
    def init_data(self):
        for role_name in self.team_config.roles_in_team:
            if role_data := self.original_data.get(role_name):
                self.data[role_name] = HighScoreTracker(score_quantity=20, highscores=role_data)
            else:
                self.data[role_name] = HighScoreTracker(score_quantity=20)

    def save_config(self):
        data = {name: data.serialize() for name, data in self.data.items()}
        self.full_data[self.team_config.name] = data

        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self.full_data, f)

    def remove_player(self, player):
        for role_name, tracker in self.data.items():
            tracker.try_remove_item(player)


class TeamDataAllRoles(TeamData):
    def init_data(self):
        for role_name in self.team_config.role_configs.keys():
            self.data[role_name] = HighScoreTracker(score_quantity=20)

    def sort_by_value(self):
        self.data = dict(sorted(self.data.items(), key=lambda x: x[1].get_value(0), reverse=True))

    def display_all_roles(self, colored=True, highlighted_name=None):
        for role_name, tracker in self.data.items():
            if not tracker.highscores:
                continue
            print(display_tracker(tracker, role_name, colored, highlighted_name))
