# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    supabase_url: str
    supabase_key: str
    n8n_webhook_url: str

    class Config:
        env_file = ".env"  # Loads variables from .env file if present