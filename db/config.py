# config.py (или отдельный runtime_settings.py)
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    dynadot_api_key: str
    crypto_pay_token: str
    db_url: str
    admins: list[int]
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
