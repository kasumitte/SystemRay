from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_SETTINGS = {
    "theme": "dark",
    "custom_prompt": "",
    "language": "en"
}

class Conf:
    DB_PATH: Path = BASE_DIR / 'data' / 'systemray.db'
    LOG_PATH: Path = BASE_DIR / 'logs' / 'system.log'
    
    @classmethod
    def init_dirs(cls):
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        