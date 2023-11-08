from dataclasses import field, dataclass
from typing import List, Dict, Literal, Tuple, get_args

from colorama import Fore, Style

ATTRIBUTE_NAME = Literal[
    'ada', 'ana d', 'att', 'def', 'det', 'fit', 'gkd', 'gkh', 'gks', 'judge a', 'judge p', 'jud sa', 'dis', 'men', 'mot', 'negotiating', 'mgm', 'phy', 'sps', 'tco', 'tac knw', 'tec', 'youth']

attribute_names: Tuple[ATTRIBUTE_NAME, ...] = get_args(ATTRIBUTE_NAME)

StaffAttributes = Dict[ATTRIBUTE_NAME, int]


def get_text_color(value):
    for max_value, style in (
            (3.5, (Fore.WHITE,)),
            (4.0, (Fore.WHITE, Style.BRIGHT)),
            (4.5, (Fore.YELLOW, Style.BRIGHT)),
            (5.0, (Fore.GREEN, Style.BRIGHT)),
            (100, (Fore.CYAN, Style.BRIGHT)),
    ):

        if max_value > value:
            return "".join(str(x) for x in style)


@dataclass
class Attr:
    name: ATTRIBUTE_NAME
    weight: int


def short_name(name:str):
    name = name.split()
    return f"{name[0][0]}. {name[-1]}"

@dataclass
class RoleConfig:
    name: str
    weighted_attributes: List[Attr]
    normalize: bool = True
    _top_staffers: Dict[str, float] = field(default_factory=lambda: {})

    def calculate_score(self, weighted_value) -> float:
        if not self.normalize:
            return weighted_value / 60
        else:
            weight_sum = sum([attribute.weight for attribute in self.weighted_attributes])
            return weighted_value / (4 * weight_sum)

    def evaluate_staffer(self, staffer: str, attributes: StaffAttributes):
        weighted_value = 0
        for weighted_attribute in self.weighted_attributes:
            weighted_value += attributes[weighted_attribute.name] * weighted_attribute.weight

        score = self.calculate_score(weighted_value)
        self.try_add_top_staffer(staffer, score)

    def output(self):

        print(f"{self.name + ':':<20} {' | '.join(f'{short_name(staffer):>20}: {get_text_color(score)}{score:3.2f}{Style.RESET_ALL}' for staffer, score in self._top_staffers.items())}")

    def try_add_top_staffer(self, staffer: str, score: float):
        self._top_staffers[staffer] = score
        self._top_staffers = {
            pair[0]: pair[1]
            for pair in
            sorted(self._top_staffers.items(), key=lambda x: x[1], reverse=True)[:7]
        }
