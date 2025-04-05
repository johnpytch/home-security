from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv


class Settings(BaseSettings):
    # Telegram configuration
    TELEGRAM_BOT_TOKEN: str
    USER_JOHN: str
    USER_S: str
    USER_R: str
    USER_A: str

    # Telegram API
    TELEGRAM_SEND_MESSAGE_URL: str = "https://api.telegram.org/bot{token}/sendMessage"
    TELEGRAM_SEND_PHOTO_URL: str = "https://api.telegram.org/bot{token}/sendPhoto"

    # Email server
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    IMAP: str = "imap.gmail.com"
    REC_SENDER: str
    DENN_SENDER: str
    SENDER_ADDRESS: str

    # Postgres
    POSTGRES_USER: str = "homesecurity"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "homesecurity"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # MinIO
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_USER: str = "homesecurity"
    MINIO_PASSWORD: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


load_dotenv(
    ".env", override=True
)  # A god send if you are on windows and can't source .env ;(
settings = Settings()
