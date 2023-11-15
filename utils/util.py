from dataclasses import field, dataclass
from typing import Dict


@dataclass
class HighScoreTracker:
    score_quantity: int = 8
    highscores: Dict[str, float] = field(default_factory=lambda: {})
    comparison_value: int = 0

    def try_add_score(self, name: str, score: float):
        self.highscores[name] = score
        self.highscores = {
            pair[0]: pair[1]
            for pair in
            sorted(self.highscores.items(), key=lambda x: x[1], reverse=True)[:self.score_quantity]
        }

    def serialize(self) -> Dict:
        return self.highscores


