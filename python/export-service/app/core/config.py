import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/notes.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXPORT_DIR = BASE_DIR / 'exports'

    # Create export directory if it doesn't exist
    EXPORT_DIR.mkdir(exist_ok=True)
