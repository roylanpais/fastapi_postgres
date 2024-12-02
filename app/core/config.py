from pydantic import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "secret key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str =  "postgresql+psycopg2://app_user:app_password@db/app"

    class Config:
        env_file = ".env"

settings = Settings()
