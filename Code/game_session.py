"""
game_session.py
manages one game round from start to finish
tracks attempts, time, hints and writes to game_log.csv when done
"""

import csv
import os
import time

from math_engine      import MathEngine
from puzzle           import Puzzle
from score_calculator import ScoreCalculator


CSV_COLUMNS = ["username", "score", "mode", "won", "time_used", "attempts", "hints_used"]
CSV_PATH    = os.path.join(os.path.dirname(__file__), "..", "data", "game_log.csv")


class GameSession:

    def __init__(self, username: str, mode: str, mode_config: dict):
        self.username    = username
        self.mode        = mode
        self.mode_config = mode_config

        # puzzle data - filled when start() is called
        self.numbers = []
        self.target  = 0

        # session stats
        self.attempts   = 0
        self.hints_used = 0
        self.time_used  = 0.0
        self.score      = 0
        self.won        = 0  # 1 = win, 0 = loss

        # internal
        self._start_time = None
        self._active     = False  # prevents double end_game() calls
        self._puzzle     = None

        # create engine - advanced mode enables ^ and sqrt
        self._engine     = MathEngine(advanced_mode=mode_config.get("advanced", False))
        self._score_calc = ScoreCalculator()

    def start(self):
        # reset counters and generate a new puzzle
        self.attempts   = 0
        self.hints_used = 0
        self.score      = 0
        self.won        = 0

        # generate solvable puzzle
        self._puzzle = Puzzle(self.mode_config)
        self._puzzle.generate()

        self.numbers = self._puzzle.numbers
        self.target  = self._puzzle.target

        # start timer
        self._start_time = time.time()
        self._active     = True

    def submit(self, expression: str) -> dict:
        # evaluate player's expression and check if correct
        if not self._active:
            return {"correct": False, "result": None, "error": "Game is not active"}

        # count every submit attempt
        self.attempts += 1

        # check player used exactly the right numbers
        number_error = self._check_numbers_used(expression)
        if number_error:
            return {"correct": False, "result": None, "error": number_error}

        # evaluate the math
        try:
            result  = self._engine.evaluate(expression)
            correct = abs(result - float(self.target)) < 1e-6
            return {"correct": correct, "result": result, "error": None}

        except ValueError as e:
            return {"correct": False, "result": None, "error": str(e)}

    def _check_numbers_used(self, expression: str) -> str:
        # extract numbers from expression and validate against puzzle numbers
        import re

        found = [int(float(n)) for n in re.findall(r"\d+(?:\.\d+)?", expression)]

        # delegate check to puzzle
        return self._puzzle.validate(found)

    def use_hint(self) -> int:
        # give player a hint - return one of the puzzle numbers
        if not self.numbers:
            return None

        self.hints_used += 1

        # return next number as hint
        index = min(self.hints_used - 1, len(self.numbers) - 1)
        return self.numbers[index]

    def end_game(self, won: bool):
        # stop timer, calculate score and save to CSV
        if not self._active:
            return
        self._active = False

        # stop timer
        elapsed        = time.time() - self._start_time
        self.time_used = max(0.0, round(elapsed, 2))

        self.won = 1 if won else 0

        # calculate final score
        self.score = self._score_calc.calculate_score(
            mode       = self.mode,
            won        = won,
            time_used  = self.time_used,
            attempts   = self.attempts,
            hints_used = self.hints_used,
        )

        # write to log file
        self._write_log()

    def _write_log(self):
        # append one row to game_log.csv
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

        file_exists = os.path.isfile(CSV_PATH)

        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)

            # write header only if file is new
            if not file_exists:
                writer.writeheader()

            writer.writerow({
                "username":   self.username,
                "score":      self.score,
                "mode":       self.mode,
                "won":        self.won,
                "time_used":  self.time_used,
                "attempts":   self.attempts,
                "hints_used": self.hints_used,
            })
