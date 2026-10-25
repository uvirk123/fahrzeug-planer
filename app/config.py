

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    api_key: str
    log_level: str = "INFO"
    max_failed_logins: int = 5
    failed_login_window_seconds: int = 60
    enable_docs: bool = True


settings = Settings()
