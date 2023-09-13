import argparse
from typing import Type

from utils.config import DefaultConfig, elements_per_row
from utils.gatherer import Gatherer, RoleGatherer
from utils.image_to_text import image_to_int, image_to_str
from utils.role_config import RoleConfig, ColorParserRoleConfig, SaveRoleConfig, UseRoleConfig
from utils.screenshot import Screenshotter, crop_from_config, crop_name_from_config
from utils.team_gatherer import TeamData

parser = argparse.ArgumentParser(description='Process command-line arguments.')
parser.add_argument('-k', '--save-key', required=False, type=str, help='Key to save value', default=None)
parser.add_argument('-r', '--save-role', required=False, type=str, help='Key to save config for a role', default=None)
parser.add_argument('-u', '--use-role', required=False, type=str, help='Key to save config for a role', default=None)
parser.add_argument('-t', '--gather-team', required=False, type=str, help='Key to save player data for best in role for a team', default=None)
parser.add_argument('-o', '--old-data', action='store_true')
parser.add_argument('-a', '--all-roles', action='store_true')
parser.add_argument('-v', '--more-data', action='store_true')
args: argparse.Namespace = parser.parse_args()


class MainProcessor:
    def __init__(self, screenshotter: Screenshotter, config: Type[DefaultConfig], args: argparse.Namespace):

        self.config: Type[DefaultConfig] = config
        self.screenshotter: Screenshotter = screenshotter
        self.player_name = image_to_str(crop_name_from_config(DefaultConfig, screenshotter)).split(" ")[-1].capitalize()

        if not args.all_roles:
            self.gatherers = [Gatherer()]
            if args.use_role:
                self.role_config: RoleConfig = UseRoleConfig(args.use_role)
            elif args.save_role:
                self.role_config: RoleConfig = SaveRoleConfig(args.save_role)
            else:
                self.role_config: RoleConfig = ColorParserRoleConfig()
        else:
            self.role_config: RoleConfig = RoleConfig()
            self.gatherers = []
            for role_name, role_config in self.role_config.read_config().items():
                self.gatherers.append(RoleGatherer(role_name, role_config))

    def gather_data(self) -> list[Gatherer]:

        for row_i in range(3):
            for attribute_number in range(elements_per_row[row_i]):
                image = crop_from_config(self.config, row_i, attribute_number, self.screenshotter)
                importance = self.role_config.get_importance(image, row_i, attribute_number)
                try:
                    # value = random.randrange(5,21)
                    value = image_to_int(image)
                except ValueError:
                    if row_i == 0 and attribute_number == elements_per_row[row_i] - 1:
                        continue  # gk has one less attribute in first row
                    raise
                for gatherer in self.gatherers:
                    gatherer.add_to_row(row_i, attribute_number, importance, value)
        self.role_config.end()
        return self.gatherers




def main():
    from colorama import init as colorama_init
    colorama_init()

    main_processor = MainProcessor(Screenshotter(), DefaultConfig, args)
    team_data = TeamData(args.gather_team) if args.gather_team else None

    gatherers = main_processor.gather_data()
    max_score = -10000000000000

    for gatherer in gatherers:
        gatherer.compile_complete_data()
        if team_data:
            team_data.add(main_processor.player_name, gatherer.role_name, gatherer.complete_data.average_value)

        if gatherer.complete_data.average_value > max_score:
            max_score = gatherer.complete_data.average_value

    if len(gatherers) < 2:
        max_score = None

    prefix_previous = None

    for gatherer in gatherers:
        prefix_current = gatherer.role_name.split("_")[0]
        if prefix_previous and prefix_current != prefix_previous:
            print("-" * 63)
        gatherer.output(args, max_score)
        prefix_previous = prefix_current
    print("-"*63)
    if team_data:
        team_data.save_config()

        for position, players in team_data.current_team_config.items():
            print(f"{position: <10}: {' | '.join([f'{player[0]}: {player[1]:6.2f}' for player in players.items()])}")


if __name__ == '__main__':
    main()
