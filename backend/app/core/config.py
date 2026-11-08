from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    APP_NAME: str = "BD Board Result and Verification API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    EBR_BASE_URL: str = "https://eboardresults.com"
    EBR_REFERER: str = "https://eboardresults.com/v2/home"

    REQUEST_TIMEOUT: int = 30

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()