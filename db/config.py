# config.py (или отдельный runtime_settings.py)
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    bot_token: str
    dynadot_api_key: str
    db_url: str
    admins: List[int]
    percent_buy_default: float = 1.4

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

class RuntimeConfig:
    percent_buy: float = settings.percent_buy_default


runtime = RuntimeConfig()