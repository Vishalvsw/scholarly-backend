from pydantic_settings import BaseSettings
from typing import List
import os
import json

class Settings(BaseSettings):
    APP_NAME: str = "Scholarly Platform"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    MONGODB_URL: str
    DATABASE_NAME: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".doc", ".docx"]
    FRONTEND_URL: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "ALLOWED_EXTENSIONS":
                return json.loads(raw_val)
            return raw_val

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
