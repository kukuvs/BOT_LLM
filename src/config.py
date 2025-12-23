from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: SecretStr

    # LLM (Mistral)
    MISTRAL_API_KEY: SecretStr
    MISTRAL_BASE_URL: str | None = None
    MISTRAL_MODEL: str = "mistral-large-latest" # Или "mistral-small-latest", "open-mistral-nemo"

    # PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    # Путь к JSON файлу (по умолчанию внутри контейнера или локально)
    DATA_JSON_PATH: str = "data/videos.json"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # Игнорировать лишние переменные в .env
    )

settings = Settings()
