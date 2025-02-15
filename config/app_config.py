from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    SLACK_BOT_TOKEN: str
    GEMINI_MODEL: str = "gemini-2.0-flash-001"
    GOOGLE_API_KEY: str
    DEBUG_MODE: bool = False
    PORT: int = 3000


app_config = AppConfig()
