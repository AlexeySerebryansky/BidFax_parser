import json
from pathlib import Path


class ProgressManager:

    def __init__(self, path: Path):
        self.path = path
        self.progress = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {}

        with self.path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(
                self.progress,
                file,
                indent=4,
                ensure_ascii=False
            )

    def get_progress(self) -> tuple[str, str, int] | None:
        if not self.progress:
            return None

        return (
            self.progress["brand"],
            self.progress["model"],
            self.progress["page"],
        )

    def save_progress(self, brand: str, model: str, page: int) -> None:

        self.progress = {
            "brand": brand,
            "model": model,
            "page": page,
        }

        self._save()
