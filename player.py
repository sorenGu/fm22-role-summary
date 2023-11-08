import argparse
import sys
from typing import Type

from utils.config import DefaultConfig, elements_per_row
from utils.gatherer import Gatherer, RoleGatherer, BaseLineGatherer
from utils.image_to_text import image_to_int, image_to_str
from utils.role_config import RoleConfig, SaveRoleConfig, RoleConfigCache
from utils.screenshot import Screenshotter, crop_from_config, crop_name_from_config
from utils.team_gatherer import TeamData

parser = argparse.ArgumentParser(description='Process command-line arguments.')
parser.add_argument('-r', '--save-role', required=False, type=str, help='Key to save config for a role', default=None)
parser.add_argument('-t', '--gather-team', required=False, type=str, help='Key team to compare', default=None)
parser.add_argument('--rm', required=False, type=str, help='Remove player from team', default=None)
parser.add_argument('-s', '--save', action='store_true')


class MainProcessor:
    is_goalkeeper = False

    def __init__(self, screenshotter: Screenshotter, config: Type[DefaultConfig], args: argparse.Namespace):

        self.config: Type[DefaultConfig] = config
        self.screenshotter: Screenshotter = screenshotter
        self.base_line_gatherer = BaseLineGatherer("base")

        if args.save_role:
            self.gatherers = [Gatherer()]
            self.role_config: RoleConfig = SaveRoleConfig(args.save_role)
        else:
            self.role_config: RoleConfig = RoleConfig()
            self.gatherers = []
            config = self.role_config.read_config()
            try:
                team_roles = config[RoleConfigCache.CURRENT_TEAM]
            except KeyError:
                print(f"team {RoleConfigCache.CURRENT_TEAM} not in config file: {RoleConfigCache.FILE}")
                sys.exit(2)
            for role_name in team_roles["teams"]:
                try:
                    self.gatherers.append(RoleGatherer(role_name, config["roles"][role_name]))
                except KeyError:
                    print(f"No configuration found for {role_name} in {RoleConfigCache.FILE}")
                    sys.exit(2)

        self.player_name = image_to_str(
            crop_name_from_config(DefaultConfig, screenshotter),
            config="-c tessedit_char_blacklist=.\\\”:\\\"-,").split(" ")[-1].capitalize()

    def gather_data(self) -> list[Gatherer]:

        for row_i in range(3):
            for attribute_number in range(elements_per_row[row_i]):
                image = crop_from_config(self.config, row_i, attribute_number, self.screenshotter)
                importance = self.role_config.get_importance(image, row_i, attribute_number)
                try:
                    value = image_to_int(image)
                    if self.is_non_gk_attribute(attribute_number, row_i) and value == 4:
                        if input("Is this a goalkeeper? (y/n)") == "y":
                            MainProcessor.is_goalkeeper = True
                            continue
                except ValueError:
                    if self.is_non_gk_attribute(attribute_number, row_i):
                        MainProcessor.is_goalkeeper = True
                        continue  # gk has one less attribute in first row
                    raise
                for gatherer in self.gatherers:
                    gatherer.add_to_row(row_i, attribute_number, value, importance)
                self.base_line_gatherer.add_to_row(row_i, attribute_number, value)
        self.role_config.end()
        return self.gatherers

    def is_non_gk_attribute(self, attribute_number, row_i):
        return row_i == 0 and attribute_number == elements_per_row[row_i] - 1


def main(team, save, args, **kwargs):
    from colorama import init as colorama_init
    colorama_init()

    if team_name := team:
        RoleConfigCache.set_team(team_name)
        if remove_player := args.rm:
            team_data = TeamData(team_name)
            team_data.remove_player(remove_player)
            team_data.save_config()
            return

    main_processor = MainProcessor(Screenshotter(), DefaultConfig, args)
    team_data = TeamData(team_name) if team_name else None

    gatherers = main_processor.gather_data()
    max_score = -10000000000000

    main_processor.base_line_gatherer.compile_complete_data()

    for gatherer in gatherers:
        if not (MainProcessor.is_goalkeeper == gatherer.role_name.startswith("GK")):
            continue

        gatherer.compile_complete_data()

        if gatherer.complete_data.average_value > max_score:
            max_score = gatherer.complete_data.average_value

    if len(gatherers) < 2:
        max_score = None

    prefix_previous = None
    print(main_processor.player_name)
    for gatherer in gatherers:
        if not (MainProcessor.is_goalkeeper == gatherer.role_name.startswith("GK")):
            continue

        gatherer.calculate_efficiency(main_processor)

        if max_score:
            gatherer.complete_data.percentage_of_max_score = 100 * gatherer.complete_data.average_value / max_score

            if team_data is not None and gatherer.complete_data.percentage_of_max_score > 96:
                team_data.add(main_processor.player_name, gatherer.role_name, gatherer.complete_data.average_value_repr)

        if gatherer.complete_data.efficiency < 105 and not (team_data is not None and gatherer.complete_data.percentage_of_max_score > 95):
            continue

        prefix_current = gatherer.role_name[:1]
        if prefix_previous and prefix_current != prefix_previous:
            print("-" * 40)

        gatherer.output(args)
        prefix_previous = prefix_current
    print("-"*40)
    if team_data:
        if save:
            team_data.save_config()
        team_data.output(main_processor.player_name)



if __name__ == '__main__':
    args: argparse.Namespace = parser.parse_args()
    if not args.gather_team and args.save_role:
        print("Use either gather-team or save_role")
        parser.print_help()
        sys.exit(2)
    main(args.gather_team, args.save, args)
