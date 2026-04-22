"""
game_stats.py
reads game_log.csv and calculates stats for the statistics page
returns plain lists and dicts - no UI code here
"""

import csv
import math
import os


CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "game_log.csv")


class StatisticsManager:

    def __init__(self, csv_path: str = CSV_PATH):
        self._csv_path = csv_path

    def get_summary_stats(self, username: str) -> dict:
        # calculate mean, median, min, max, stdev for attempts and hints_used
        logs = self._get_logs(username)
        if not logs:
            return {"attempts": {}, "hints_used": {}}

        attempts_vals   = []
        hints_used_vals = []

        for row in logs:
            attempts_vals.append(self._int(row, "attempts"))
            hints_used_vals.append(self._int(row, "hints_used"))

        return {
            "attempts":   self._compute_stats(attempts_vals),
            "hints_used": self._compute_stats(hints_used_vals),
        }

    def get_attempts_distribution(self, username: str) -> list:
        # return list of attempts values for histogram
        return [self._int(row, "attempts") for row in self._get_logs(username)]

    def get_time_series(self, username: str) -> list:
        # return time_used values in session order for line chart
        return [self._float(row, "time_used") for row in self._get_logs(username)]

    def get_scatter_data(self, username: str) -> list:
        # return attempts and time_used pairs for scatter plot
        return [
            {
                "attempts":  self._int(row, "attempts"),
                "time_used": self._float(row, "time_used"),
            }
            for row in self._get_logs(username)
        ]

    def get_win_ratio(self, username: str) -> dict:
        # return win/loss count and win rate percentage for pie chart
        logs     = self._get_logs(username)
        total    = len(logs)
        wins     = sum(1 for row in logs if self._int(row, "won") == 1)
        losses   = max(0, total - wins)
        win_rate = round((wins / total) * 100, 2) if total > 0 else 0.0
        return {"wins": wins, "losses": losses, "win_rate": win_rate}

    def get_hints_bar(self, username: str) -> list:
        # return hints_used per session for bar chart
        return [self._int(row, "hints_used") for row in self._get_logs(username)]

    def _get_logs(self, username: str) -> list:
        # read CSV and return only rows for this user
        username = username.strip()
        if not username:
            return []

        if not os.path.isfile(self._csv_path):
            return []

        try:
            with open(self._csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return [
                    row for row in reader
                    if row.get("username", "").strip() == username
                ]
        except (OSError, csv.Error):
            return []

    def _read_logs(self) -> list:
        # read all rows unfiltered
        if not os.path.isfile(self._csv_path):
            return []
        try:
            with open(self._csv_path, "r", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except (OSError, csv.Error):
            return []

    def _filter_user_logs(self, username: str) -> list:
        return self._get_logs(username)

    def _compute_stats(self, values: list) -> dict:
        # calculate basic statistics for a list of numbers
        if not values:
            return {}

        n    = len(values)
        mean = sum(values) / n

        # find median
        sorted_values = sorted(values)
        mid           = n // 2
        if n % 2 == 1:
            median = float(sorted_values[mid])
        else:
            median = (sorted_values[mid - 1] + sorted_values[mid]) / 2.0

        # calculate standard deviation
        variance = sum((v - mean) ** 2 for v in values) / n
        stdev    = math.sqrt(max(0.0, variance))

        return {
            "mean":   round(mean, 4),
            "median": round(median, 4),
            "min":    min(values),
            "max":    max(values),
            "stdev":  round(stdev, 4),
        }

    def _int(self, row: dict, field: str) -> int:
        # safely get int from CSV row, return 0 if fails
        try:
            return int(str(row.get(field, 0)).strip())
        except (ValueError, TypeError):
            return 0

    def _float(self, row: dict, field: str) -> float:
        # safely get float from CSV row, return 0.0 if fails
        try:
            return float(str(row.get(field, 0.0)).strip())
        except (ValueError, TypeError):
            return 0.0
