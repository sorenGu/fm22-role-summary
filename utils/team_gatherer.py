import json
from json import JSONDecodeError

from colorama import Style, Fore, Back

from utils.gatherer import get_text_color
from utils.role_config import RoleConfig


class TeamData:
    CONFIG_FILE = "team_data.json"

    def __init__(self, team_name: str):
        self.team_name = team_name
        self.config = self.read_config()
        self.current_team_config = self.config.get(team_name, {})
        self.update_config_keys()

    def save_config(self):
        self.config[self.team_name] = self.current_team_config

        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self.config, f)

    @classmethod
    def read_config(cls):
        try:
            with open(cls.CONFIG_FILE, "r") as f:
                return json.load(f)
        except (JSONDecodeError, FileNotFoundError) as e:
            return {}

    def update_config_keys(self):
        for key in RoleConfig().read_config():
            if key not in self.current_team_config:
                self.current_team_config[key] = {}

    def add(self, player_name, position, value):
        self.current_team_config[position][player_name] = value
        self.current_team_config[position] = {
            pair[0]: pair[1]
            for pair in
            sorted(self.current_team_config[position].items(), key=lambda x: x[1], reverse=True)[:8]
        }

    def output(self, current_player):
        print(current_player)
        for position, players in self.current_team_config.items():
            players_string = ' | '.join([
                f'{player[0] if player[0] != current_player else f"{Back.LIGHTBLACK_EX}{Style.BRIGHT}{player[0]: <12}{Style.RESET_ALL}": <12}: '
                f'{get_text_color(player[1])}{player[1]:6.2f}{Style.RESET_ALL}'
                for player in players.items()
            ])
            print(f"{position: <10}- {players_string}")
