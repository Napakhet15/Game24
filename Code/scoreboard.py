import json
import os


SCOREBOARD_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "scoreboard.json")


class ScoreboardManager:

    def __init__(self, path: str = SCOREBOARD_PATH):
        self.path = path

    def add_score(self, username: str, score: int, mode: str):
        # top 20
        entries = self._load()

        entries.append({
            "username": username,
            "score":    score,
            "mode":     mode,
        })

        entries = self._trim_top_20(entries)
        self._save(entries)

    def _load(self) -> list:
        if not os.path.isfile(self.path):
            return []

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, entries: list):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)

    def _trim_top_20(self, entries: list) -> list:
        # sort score top 20
        sorted_entries = sorted(entries, key=lambda e: e["score"], reverse=True)
        return sorted_entries[:20]
