import os
import platform as _platform
from pathlib import Path


def _is_wsl() -> bool:
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except Exception:
        return False


def _win_to_wsl(win_path: str) -> str:
    if not win_path:
        return win_path
    if len(win_path) >= 2 and win_path[1] == ":":
        drive = win_path[0].lower()
        rest = win_path[2:].replace("\\", "/")
        return f"/mnt/{drive}{rest}"
    return win_path


def _resolve_path(win_path: str, wsl_path: str) -> str:
    if _is_wsl():
        return wsl_path
    return win_path


_USERNAME = "zccyman"


class Config:
    BACKUP_BASE_DIR = os.getenv(
        "CHAT_BACKUP_DIR",
        _resolve_path(r"D:\backup\chat-records", "/mnt/d/backup/chat-records"),
    )

    WECHAT_SOURCE_DIR = os.getenv(
        "WECHAT_SOURCE_DIR",
        _resolve_path(
            rf"C:\Users\{_USERNAME}\Documents\WeChat Files",
            f"/mnt/c/Users/{_USERNAME}/Documents/WeChat Files",
        ),
    )
    QQ_SOURCE_DIR = os.getenv(
        "QQ_SOURCE_DIR",
        _resolve_path(
            rf"C:\Users\{_USERNAME}\Documents\Tencent Files",
            f"/mnt/c/Users/{_USERNAME}/Documents/Tencent Files",
        ),
    )
    FEISHU_SOURCE_DIR = os.getenv(
        "FEISHU_SOURCE_DIR",
        _resolve_path(
            rf"C:\Users\{_USERNAME}\AppData\Roaming\LarkShell",
            f"/mnt/c/Users/{_USERNAME}/AppData/Roaming/LarkShell",
        ),
    )

    WECHAT_DB_KEY = os.getenv("WECHAT_DB_KEY", "")
    QQ_DB_KEY = os.getenv("QQ_DB_KEY", "")

    FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
    FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")

    PLATFORMS = ["wechat", "qq", "feishu"]

    SOURCE_PATTERNS = {
        "wechat": {
            "db_dirs": ["Msg", "Msg/Multi"],
            "db_files": [
                "Msg/MicroMsg.db",
                "Msg/ChatMsg.db",
                "Msg/Contact.db",
                "Msg/Misc.db",
                "Msg/Emotion.db",
                "Msg/Media.db",
                "Msg/OpenIMMsg.db",
                "Msg/OpenIMContact.db",
                "Msg/PublicMsg.db",
            ],
            "db_glob": ["Msg/Multi/MSG*.db", "Msg/Multi/MediaMSG*.db"],
            "exclude_suffixes": ["-shm", "-wal", "-journal"],
        },
        "qq": {
            "db_dirs": ["nt_qq/nt_db"],
            "db_files": [
                "nt_qq/nt_db/nt_msg.db",
                "nt_qq/nt_db/group_info.db",
                "nt_qq/nt_db/profile_info.db",
                "nt_qq/nt_db/buddy_msg_fts.db",
                "nt_qq/nt_db/group_msg_fts.db",
                "nt_qq/nt_db/misc.db",
                "nt_qq/nt_db/emoji.db",
                "nt_qq/nt_db/collection.db",
                "nt_qq/nt_db/file_assistant.db",
                "nt_qq/nt_db/files_in_chat.db",
            ],
            "db_glob": [],
            "exclude_suffixes": [
                "-shm",
                "-wal",
                "-journal",
                "-first.material",
                "-last.material",
            ],
        },
        "feishu": {
            "db_dirs": [],
            "db_files": [],
            "db_glob": [],
            "exclude_suffixes": ["-shm", "-wal", "-journal"],
        },
    }

    @classmethod
    def get_backup_dir(cls, platform: str) -> str:
        return os.path.join(cls.BACKUP_BASE_DIR, platform)

    @classmethod
    def get_source_dir(cls, platform: str) -> str:
        mapping = {
            "wechat": cls.WECHAT_SOURCE_DIR,
            "qq": cls.QQ_SOURCE_DIR,
            "feishu": cls.FEISHU_SOURCE_DIR,
        }
        return mapping.get(platform, "")

    @classmethod
    def get_meta_path(cls, platform: str) -> str:
        return os.path.join(cls.get_backup_dir(platform), "backup_meta.json")


config = Config()
