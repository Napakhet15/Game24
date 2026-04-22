"""
achievements.py
checks and unlocks achievements after each game session
reads game_log.csv and saves unlocked achievements to users.json
"""

import csv
import os

from auth import UserStore


CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "game_log.csv")


class AchievementManager:

    def __init__(self, store: UserStore = None, csv_path: str = CSV_PATH):
        self._store    = store if store is not None else UserStore()
        self._csv_path = csv_path

    def evaluate(self, user) -> list:
        # check all achievements and unlock new ones for this user
        logs = self._filter_user_logs(user.username)

        newly_unlocked = []

        for achievement_id, check_fn in self._all_checks():

            # skip already unlocked
            if achievement_id in user.achievements:
                continue

            # run the check
            if check_fn(logs):
                user.achievements.append(achievement_id)
                newly_unlocked.append(achievement_id)

        # save only if something changed
        if newly_unlocked:
            self._store.save_user(user)

        return newly_unlocked

    def _read_logs(self) -> list:
        # read all rows from game_log.csv
        if not os.path.isfile(self._csv_path):
            return []

        rows = []
        try:
            with open(self._csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(row)
        except Exception:
            return []

        return rows

    def _filter_user_logs(self, username: str) -> list:
        # get only rows for this user
        all_rows = self._read_logs()
        return [
            row for row in all_rows
            if row.get("username", "").strip() == username
        ]

    def _count_wins(self, logs: list) -> int:
        # count total wins
        return sum(1 for row in logs if self._is_win(row))

    def _check_streak(self, logs: list, length: int = 3) -> bool:
        # check if last 'length' sessions are all wins
        if len(logs) < length:
            return False
        recent = logs[-length:]
        return all(self._is_win(row) for row in recent)

    # each method below checks one achievement condition

    def _check_first_blood(self, logs: list) -> bool:
        # win at least 1 game
        return self._count_wins(logs) >= 1

    def _check_getting_warmed_up(self, logs: list) -> bool:
        # play at least 10 games total
        return len(logs) >= 10

    def _check_marathon(self, logs: list) -> bool:
        # play at least 50 games total
        return len(logs) >= 50

    def _check_all_rounder(self, logs: list) -> bool:
        # win at least once in every mode
        modes_won = {row.get("mode", "").strip()
                     for row in logs if self._is_win(row)}
        required  = {"classic", "hard", "advanced", "speed", "practice"}
        return required.issubset(modes_won)

    def _check_no_hint_master(self, logs: list) -> bool:
        # win 10 games without using any hints
        count = sum(
            1 for row in logs
            if self._is_win(row) and self._int(row, "hints_used") == 0
        )
        return count >= 10

    def _check_hot_streak(self, logs: list) -> bool:
        # win 3 games in a row
        return self._check_streak(logs, length=3)

    def _check_diamond_mind(self, logs: list) -> bool:
        # reach total score of 5000 across all sessions
        total = sum(self._int(row, "score") for row in logs)
        return total >= 5000

    def _check_unbreakable(self, logs: list) -> bool:
        # play 20+ games with win rate >= 75%
        total = len(logs)
        if total < 20:
            return False
        win_rate = self._count_wins(logs) / total
        return win_rate >= 0.75

    def _all_checks(self) -> list:
        # list of all achievements and their check functions
        return [
            ("first_blood",        self._check_first_blood),
            ("getting_warmed_up",  self._check_getting_warmed_up),
            ("marathon",           self._check_marathon),
            ("all_rounder",        self._check_all_rounder),
            ("no_hint_master",     self._check_no_hint_master),
            ("hot_streak",         self._check_hot_streak),
            ("diamond_mind",       self._check_diamond_mind),
            ("unbreakable",        self._check_unbreakable),
        ]

    def _is_win(self, row: dict) -> bool:
        # check if this session was a win
        return self._int(row, "won") == 1

    def _int(self, row: dict, field: str) -> int:
        # safely get int value from CSV row
        try:
            return int(row.get(field, 0))
        except (ValueError, TypeError):
            return 0
