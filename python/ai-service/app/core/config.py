from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings and configuration
    """
    # Application
    APP_NAME: str = "AI Speech-to-Text Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Whisper Configuration
    WHISPER_MODEL_PATH: str = "./models/ggml-base.en.bin"
    WHISPER_MODEL_SIZE: str = "base.en"  # tiny, base, small, medium, large
    WHISPER_THREADS: int = 4
    WHISPER_PROCESSORS: int = 1
    
    # Audio Processing
    MAX_FILE_SIZE_MB: int = 25
    TEMP_DIR: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
