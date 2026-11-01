import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


@dataclass(frozen=True)
class Settings:
    database_url: str | None
    cors_origins: list[str]
    admin_api_key: str | None
    document_storage_path: Path | None = None


settings = Settings(
    database_url=os.getenv("DATABASE_URL"),
    cors_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()],
    admin_api_key=os.getenv("ADMIN_API_KEY"),
    document_storage_path=Path(os.environ["DOCUMENT_STORAGE_PATH"]).expanduser() if os.getenv("DOCUMENT_STORAGE_PATH") else None,
)
