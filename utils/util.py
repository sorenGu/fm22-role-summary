from dataclasses import field, dataclass
from typing import Dict

from colorama import Style

from utils.gatherer import get_text_color


def display_name(name: str, score: float):
    return f'{name}: {score:3.2f}'

def display_name_with_color(name: str, score: float):
    return f'{name}: {get_text_color(score)}{score:6.2f}{Style.RESET_ALL}'


@dataclass
class HighScoreTracker:
    score_quantity = 8
    _highscores: Dict[str, float] = field(default_factory=lambda: {})

    def try_add_score(self, name: str, score: float):
        self._highscores[name] = score
        self._highscores = {
            pair[0]: pair[1]
            for pair in
            sorted(self._highscores.items(), key=lambda x: x[1], reverse=True)[:self.score_quantity]
        }

    def output(self, name, display_function=display_name_with_color):
        return f"{name + ':':<13} {' | '.join(display_function(name, score) for name, score in self._highscores.items())}"
