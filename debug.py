import sys

import colorama
from PIL import Image
from colorama import Fore, Style, Back

from utils.config import DefaultConfig
from utils.image_to_text import image_to_int, image_to_str
from utils.role_config import get_relevant_pixel
from utils.screenshot import Screenshotter, crop_from_config, crop_name_from_config


def parse_image(x, y, show_image=False):
    screenshotter = Screenshotter()
    image = crop_from_config(DefaultConfig, x, y, screenshotter)
    try:
        print(y, image_to_int(image), get_relevant_pixel(image))
    except Exception as e:
        print(f"failed to parse image {e}")

    if show_image:
        image.show()


def parse_row(row_i):
    for i in range(14 if row_i < 2 else 8):
        parse_image(row_i, i)

# class TeamData:
#     def __init__(self):
#         self.current_team_config = {"a": {}}
#
#     def add(self, player_name, position, value):
#         self.current_team_config[position][player_name] = value
#         self.current_team_config[position] = {
#             pair[0]: pair[1]
#             for pair in
#             sorted(self.current_team_config[position].items(), key=lambda x: x[1], reverse=True)[:5]
#         }


def parse_name():
    screenshotter = Screenshotter()
    image = crop_name_from_config(DefaultConfig, screenshotter)
    image.show()
    print(image_to_str(image))


if __name__ == "__main__":
    from colorama import init as colorama_init
    colorama_init()

    if len(sys.argv) == 1:
        parse_name()
    elif len(sys.argv) == 2:
        parse_row(int(sys.argv[1]))
    else:
        parse_image(*[int(x) for x in sys.argv[1:]], True)
