import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI Services API"

    # File Upload Configuration
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "outputs")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB

    # Whisper Configuration
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large

    # Google Cloud Configuration
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Tesseract Configuration
    TESSERACT_CMD: Optional[str] = os.getenv("TESSERACT_CMD", None)

    def __init__(self):
        # Create directories if they don't exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)


settings = Settings()
