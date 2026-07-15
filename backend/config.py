import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "").strip().lower()  # "anthropic" | "gemini" | "" (auto)

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    EXPORT_FOLDER = os.path.join(BASE_DIR, "exports")
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf", "docx"}
