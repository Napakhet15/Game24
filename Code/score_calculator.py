class ScoreCalculator:

    def __init__(self):
        self.baseScore = 100  

    def calculate_score(self, mode: str, won: bool,
                        time_used: float, attempts: int, hints_used: int) -> int:
        # lost , practice mode
        if not won or mode == "practice":
            return 0

        return self.apply_bonus(time_used, attempts, hints_used)

    def apply_bonus(self, time_used: float, attempts: int, hints_used: int) -> int:

        # faster
        time_bonus = max(0.0, 30.0 - time_used) * 2

        # first attempt
        attempt_penalty = max(0, attempts - 1) * 5

        # hint
        hint_penalty = hints_used * 10

        score = self.baseScore + time_bonus - attempt_penalty - hint_penalty

        # score
        return max(0, int(score))
