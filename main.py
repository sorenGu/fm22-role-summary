import argparse
from typing import Type

from utils.config import DefaultConfig, elements_per_row
from utils.gatherer import Gatherer, RoleGatherer
from utils.image_to_text import image_to_int, image_to_str
from utils.role_config import RoleConfig, ColorParserRoleConfig, SaveRoleConfig, UseRoleConfig, RoleConfigCache
from utils.screenshot import Screenshotter, crop_from_config, crop_name_from_config
from utils.team_gatherer import TeamData

parser = argparse.ArgumentParser(description='Process command-line arguments.')
parser.add_argument('-k', '--save-key', required=False, type=str, help='Key to save value', default=None)
parser.add_argument('-r', '--save-role', required=False, type=str, help='Key to save config for a role', default=None)
parser.add_argument('-u', '--use-role', required=False, type=str, help='Key to save config for a role', default=None)
parser.add_argument('-t', '--gather-team', required=False, type=str, help='Key team to compare', default=None)
parser.add_argument('--rm', required=False, type=str, help='Remove player from team', default=None)
parser.add_argument('-s', '--save-team', action='store_true')
parser.add_argument('-o', '--old-data', action='store_true')
parser.add_argument('-a', '--all-roles', action='store_true')
parser.add_argument('-v', '--more-data', action='store_true')
args: argparse.Namespace = parser.parse_args()


class MainProcessor:
    IS_GOALKEEPER = False

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
                        MainProcessor.IS_GOALKEEPER = True
                        continue  # gk has one less attribute in first row
                    raise
                for gatherer in self.gatherers:
                    gatherer.add_to_row(row_i, attribute_number, importance, value)
        self.role_config.end()
        return self.gatherers




def main():
    from colorama import init as colorama_init
    colorama_init()

    if team_name := args.gather_team:
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

    for gatherer in gatherers:
        gatherer.compile_complete_data()

        if gatherer.complete_data.average_value > max_score:
            max_score = gatherer.complete_data.average_value

    if len(gatherers) < 2:
        max_score = None

    prefix_previous = None
    print(main_processor.player_name)
    for gatherer in gatherers:
        if max_score:
            gatherer.complete_data.percentage_of_max_score = 100 * gatherer.complete_data.average_value / max_score
            if not (MainProcessor.IS_GOALKEEPER == gatherer.role_name.startswith("GK")):
                continue

            if team_data is not None and gatherer.complete_data.percentage_of_max_score > 85:
                team_data.add(main_processor.player_name, gatherer.role_name, gatherer.complete_data.average_value)

        prefix_current = gatherer.role_name[:1]
        if prefix_previous and prefix_current != prefix_previous:
            print("-" * 63)

        gatherer.output(args)
        prefix_previous = prefix_current
    print("-"*63)
    if team_data:
        if args.save_team:
            team_data.save_config()
        team_data.output(main_processor.player_name)



if __name__ == '__main__':
    main()
