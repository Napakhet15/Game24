"""
score_calculator.py
calculates player score after each game session

formula:
  base = 100
  time bonus = max(0, 30 - time_used) * 2
  attempt penalty = (attempts - 1) * 5
  hint penalty = hints_used * 10
  final = max(0, base + time_bonus - attempt_penalty - hint_penalty)

practice mode and loss always give 0
"""


class ScoreCalculator:

    def __init__(self):
        self.baseScore = 100  # everyone starts with 100
        self.timeBonus = 0.0  # updated each calculation

    def calculate_score(self, mode: str, won: bool,
                        time_used: float, attempts: int, hints_used: int) -> int:
        # return 0 if player lost or in practice mode
        if not won or mode == "practice":
            return 0

        return self.apply_bonus(time_used, attempts, hints_used)

    def apply_bonus(self, time_used: float, attempts: int, hints_used: int) -> int:
        # calculate time bonus and subtract penalties

        # faster = more bonus, slower than 30s = no bonus
        self.timeBonus = max(0.0, 30.0 - time_used) * 2

        # first attempt is free, each extra costs 5 points
        attempt_penalty = max(0, attempts - 1) * 5

        # each hint costs 10 points
        hint_penalty = hints_used * 10

        score = self.baseScore + self.timeBonus - attempt_penalty - hint_penalty

        # score can't go below 0
        return max(0, int(score))
