import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def _user_file(user_id: int, prefix: str) -> Path:
    return DATA_DIR / f"{prefix}_{user_id}.json"


def load_json(path: Path, default=None):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default or {}


def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_favorites(user_id: int) -> dict:
    return load_json(_user_file(user_id, "favorites"), {"favorites": []})


def save_favorites(user_id: int, data: dict):
    save_json(_user_file(user_id, "favorites"), data)
