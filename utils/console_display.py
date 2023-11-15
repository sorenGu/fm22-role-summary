from typing import Optional

from colorama import Back, Style, Fore

from utils.util import HighScoreTracker

from colorama import init as colorama_init

colorama_init()

def get_text_color(value):
    for max_value, style in (
            (0, (Fore.WHITE,)),
            (20, (Fore.WHITE, Style.BRIGHT)),
            (25, (Fore.YELLOW,)),
            (30, (Fore.YELLOW, Style.BRIGHT)),
            (35, (Fore.GREEN,)),
            (40, (Fore.GREEN, Style.BRIGHT)),
            (45, (Fore.CYAN,)),
            (50, (Fore.CYAN, Style.BRIGHT)),
            (55, (Fore.RED,)),
            (60, (Fore.RED, Style.BRIGHT)),
    ):
        if max_value > value:
            return "".join(str(x) for x in style)
    return "".join(str(x) for x in (Fore.MAGENTA, Style.BRIGHT))


def get_text_color_small(value):
    default = "".join(str(x) for x in (Fore.MAGENTA, Style.BRIGHT))
    for max_value, style in (
            (0, (Fore.WHITE,)),
            (3, (Fore.WHITE, Style.BRIGHT)),
            (6, (Fore.YELLOW, Style.BRIGHT)),
            (9, (Fore.GREEN, Style.BRIGHT)),
            (12, (Fore.CYAN, Style.BRIGHT)),
    ):
        try:
            if max_value > value:
                return "".join(str(x) for x in style)
        except TypeError:
            return default
    return default


def display_name(name: Optional[str], score: float, highlighted_name=None):
    name = f"{name}: " if name else ""
    return f'{name}{score:3.2f}'


def display_name_with_color(name: Optional[str], score: float, highlighted_name=None):
    name = f"{name:>15}: " if name else ""
    if highlighted_name and highlighted_name in name:
        name = f"{Back.LIGHTBLACK_EX}{Style.BRIGHT}{name}{Style.RESET_ALL}"
    return f'{name}{get_text_color(score)}{score:6.2f}{Style.RESET_ALL}'


def display_tracker(tracker: HighScoreTracker, name, colored=True, highlighted_name=None, compact_display=True):
    if colored:
        display_function = display_name_with_color
    else:
        display_function = display_name

    comparison_display = display_function(None, tracker.comparison_value) if tracker.comparison_value != 0 else ""

    output = f"{name + ':':<13}{comparison_display}"
    for i, data in enumerate(tracker.highscores.items()):
        name, score = data
        output += " " + display_function(name, score, highlighted_name) + " |"
        if i % 8 == 7:
            if compact_display:
                break
            output += "\n" + 13 * " "
    return output


def display_normalized_attributes(value):
    return f"{get_text_color(value)}{value:6.2f}{Style.RESET_ALL}"


def display_role_values(role_name, normalized, efficiency, percentage_from_max):
    percentage_from_max = "  *  " if percentage_from_max > 99.9 else f"{percentage_from_max:4.1f}%"

    return f"{role_name: <10}: {display_normalized_attributes(normalized)} {percentage_from_max}{Style.RESET_ALL} eff: {get_text_color_small(efficiency - 100)}{efficiency:4.1f}%{Style.RESET_ALL}"
