import sys

from PIL import Image

from utils.config import DefaultConfig
from utils.image_to_text import image_to_int, image_to_str
from utils.role_config import get_relevant_pixel, ColorRoleGetter
from utils.screenshot import ConfiguredScreenshotter


def parse_image(image: Image.Image, config: ColorRoleGetter, show_image=False):

    try:
        print(image_to_int(image), get_relevant_pixel(image), config.get_importance(image))
    except Exception as e:
        print(f"failed to parse image {e}")

    if show_image:
        image.show()


def parse_all(screenshotter: ConfiguredScreenshotter, config, show: bool):
    for attribute_image in screenshotter.iterate_attribute_images():
        parse_image(attribute_image, config, show)


def parse_name(screenshotter: ConfiguredScreenshotter):

    image = screenshotter.get_name_image()
    image.show()
    print(f"Name is: {image_to_str(image)}")


if __name__ == "__main__":
    from colorama import init as colorama_init
    colorama_init()

    _screenshotter = ConfiguredScreenshotter(DefaultConfig)
    if len(sys.argv) == 1:
        parse_name(_screenshotter)
        sys.exit()

    argument = sys.argv[1].lower()
    config = ColorRoleGetter(DefaultConfig)
    if argument in ["show", "all"]:
        parse_all(_screenshotter, config, argument == "Show")
    else:
        attribute_number = int(sys.argv[1])
        image = list(_screenshotter.iterate_attribute_images())[attribute_number]
        parse_image(image, config, True)
