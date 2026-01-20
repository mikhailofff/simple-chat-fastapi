import os

from dotenv import load_dotenv

load_dotenv()

# Database configuration
POSTGRES_USER: str = os.getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
DB_HOST: str = os.getenv("DB_HOST", "")
DB_PORT: str = os.getenv("DB_PORT", "")
POSTGRES_DB: str = os.getenv("POSTGRES_DB", "")
DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"

# Redis configuration
REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
REDIS_PORT: str = os.getenv("REDIS_PORT", "6379")

# Security
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
