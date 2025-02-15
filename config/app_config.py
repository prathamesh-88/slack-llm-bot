from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    GEMINI_MODEL: str = "gemini-2.0-flash-001"
    GOOGLE_API_KEY: str
    DEBUG_MODE: bool = False
    PORT: int = 3000

    # Slack configs
    SLACK_CLIENT_ID: str
    SLACK_CLIENT_SECRET: str
    SLACK_REDIRECT_URI: str


app_config = AppConfig()
