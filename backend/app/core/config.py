import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "MEXA"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mexa.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tu-clave-secreta-super-segura-cambiar-en-produccion")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()