import os
from pathlib import Path


class Config:
    KILO_CODE_DB_PATH = os.getenv(
        "KILO_CODE_DB_PATH", str(Path.home() / ".local" / "share" / "kilo" / "kilo.db")
    )
    OPENCODE_DB_PATH = os.getenv(
        "OPENCODE_DB_PATH", str(Path.home() / ".local" / "share" / "opencode" / "opencode.db")
    )

    @classmethod
    def get_db_path(cls, source: str = "kilo") -> str:
        if source == "opencode":
            return cls.OPENCODE_DB_PATH
        return cls.KILO_CODE_DB_PATH

    @classmethod
    def get_available_sources(cls) -> list:
        sources = []
        if os.path.exists(cls.KILO_CODE_DB_PATH):
            sources.append("kilo")
        if os.path.exists(cls.OPENCODE_DB_PATH):
            sources.append("opencode")
        return sources


config = Config()
