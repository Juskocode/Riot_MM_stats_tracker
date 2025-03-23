from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    RIOT_API_KEY: str = Field(..., validation_alias="RIOT_API_KEY")
    API_BASE_URL: str = "https://europe.api.riotgames.com"
    REQUEST_TIMEOUT: int = 10
    MAX_RETRIES: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )