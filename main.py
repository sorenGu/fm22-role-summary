import argparse
import random
from typing import Type

from utils.config import DefaultConfig, elements_per_row
from utils.gatherer import Gatherer, RoleGatherer
from utils.image_to_text import image_to_int
from utils.role_config import RoleConfig, ColorParserRoleConfig, SaveRoleConfig, UseRoleConfig
from utils.screenshot import Screenshotter

parser = argparse.ArgumentParser(description='Process command-line arguments.')
parser.add_argument('-k', '--save-key', required=False, type=str, help='Key to save value', default=None)
parser.add_argument('-r', '--save-role', required=False, type=str, help='Key to save config for a role', default=None)
parser.add_argument('-u', '--use-role', required=False, type=str, help='Key to save config for a role', default=None)
parser.add_argument('-o', '--old-data', action='store_true')
parser.add_argument('-a', '--all-roles', action='store_true')
parser.add_argument('-v', '--more-data', action='store_true')
args: argparse.Namespace = parser.parse_args()




class MainProcessor:
    def __init__(self, screenshotter: Screenshotter, config: Type[DefaultConfig], args: argparse.Namespace):
        self.config: Type[DefaultConfig] = config
        self.screenshotter: Screenshotter = screenshotter

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
                image = self.crop_from_config(self.config, row_i, attribute_number, self.screenshotter)
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

    def crop_from_config(self, config, row_i, attribute_number, screenshotter):
        row_start = config.rows_starts[row_i]
        top_start = config.top + attribute_number * (config.height + config.height_between)
        padding = 8
        return screenshotter.get_crop(
            [row_start,
             top_start - padding,
             row_start + config.width,
             top_start + config.height + padding
             ])


def main():
    main_processor = MainProcessor(Screenshotter(), DefaultConfig, args)
    
    gatherers = main_processor.gather_data()
    max_score = -10000000000000

    for i, gatherer in enumerate(gatherers):
        gatherer.compile_complete_data()
        if gatherer.complete_data.average_value > max_score:
            max_score = gatherer.complete_data.average_value

    if len(gatherers) < 2:
        max_score = None

    for i, gatherer in enumerate(gatherers):
        if i != 0 and i % 3 == 0:
            print("-"*57)
        gatherer.output(args, max_score)
    print("-"*57)


if __name__ == '__main__':
    main()
