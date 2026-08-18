from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
PROJECT_ROOT = BASE_DIR.parent  # PipocaBot_WhatsApp/
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_business_account_id: str = ""
    whatsapp_verify_token: str = ""

    google_calendar_id: str = ""
    google_credentials_path: str = str(BASE_DIR / "credentials" / "google_credentials.json")

    database_url: str = f"sqlite:///{DATA_DIR / 'pipoca.db'}"

    admin_phone_number: str = ""
    horario_abertura: str = "08:00"
    horario_fechamento: str = "21:00"

    app_secret_key: str = ""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
