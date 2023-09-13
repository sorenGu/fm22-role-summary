import sys

from utils.config import DefaultConfig
from utils.image_to_text import image_to_int
from utils.role_config import get_relevant_pixel
from utils.screenshot import Screenshotter, crop_from_config


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


if __name__ == "__main__":
    if len(sys.argv) == 2:
        parse_row(int(sys.argv[1]))
    else:
        parse_image(*[int(x) for x in sys.argv[1:]], True)
