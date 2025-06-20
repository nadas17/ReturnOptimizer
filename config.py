# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = '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'
    supabase_url: str = 'https://dqebwcrudfbduplnydby.supabase.co'
    supabase_key: str = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxZWJ3Y3J1ZGZiZHVwbG55ZGJ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAyNDE3MDQsImV4cCI6MjA2NTgxNzcwNH0.QJoDusiyOhC92QanAL1HYrDZiIpSRcqUWVuCdJhnVmo'
    n8n_webhook_url: str = "https://dogukangultekin.app.n8n.cloud/webhook-test/1266e9f9-6bb7-481e-a5b5-0a4e392e9b69"
    class Config:
        env_file = ".env"

settings = Settings()