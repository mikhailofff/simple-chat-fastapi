from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class ConfigDict:
        env_file = "../.env"


settings = Settings()
