from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()  # Explicitly load the .env file

class Settings(BaseSettings):
    POSTGRES_HOSTNAME: Optional[str] = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "ingest_test"
    DATABASE_PORT: int = 5432

    class Config:
        env_file = ".env"


settings = Settings()
