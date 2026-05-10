import csv
import math
import os


CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "game_log.csv")


class StatisticsManager:

    def __init__(self, csv_path: str = CSV_PATH):
        self._csv_path = csv_path

    def get_summary_stats(self, username: str) -> dict:
        # calculate 
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
        # histogram
        return [self._int(row, "attempts") for row in self._get_logs(username)]

    def get_time_series(self, username: str) -> list:
        # line chart
        return [self._float(row, "time_used") for row in self._get_logs(username)]

    def get_scatter_data(self, username: str) -> list:
        # scatter plot
        return [
            {
                "attempts":  self._int(row, "attempts"),
                "time_used": self._float(row, "time_used"),
            }
            for row in self._get_logs(username)
        ]

    def get_win_ratio(self, username: str) -> dict:
        # pie chart
        logs     = self._get_logs(username)
        total    = len(logs)
        wins     = sum(1 for row in logs if self._int(row, "won") == 1)
        losses   = max(0, total - wins)
        win_rate = round((wins / total) * 100, 2) if total > 0 else 0.0
        return {"wins": wins, "losses": losses, "win_rate": win_rate}

    def get_hints_bar(self, username: str) -> list:
        # bar chart
        return [self._int(row, "hints_used") for row in self._get_logs(username)]

    def _get_logs(self, username: str) -> list:
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
        # calculate statistics
        if not values:
            return {}

        n    = len(values)
        mean = sum(values) / n

        sorted_values = sorted(values)
        mid           = n // 2
        if n % 2 == 1:
            median = float(sorted_values[mid])
        else:
            median = (sorted_values[mid - 1] + sorted_values[mid]) / 2.0

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
        try:
            return int(str(row.get(field, 0)).strip())
        except (ValueError, TypeError):
            return 0

    def _float(self, row: dict, field: str) -> float:
        try:
            return float(str(row.get(field, 0.0)).strip())
        except (ValueError, TypeError):
            return 0.0
