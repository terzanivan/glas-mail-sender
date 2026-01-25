from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POCKETBASE_URL: str = "http://localhost:8090"
    POCKETBASE_ADMIN: str = ""
    POCKETBASE_ADMIN_PW: str = ""

    MAILTRAP_API_TOKEN: str = ""
    MAILTRAP_HOST: str = "smtp.mailtrap.io"
    MAILTRAP_PORT: int = 2525
    MAILTRAP_USER: str = ""
    MAILTRAP_PASSWORD: str = ""

    # Local Mail Sandbox (Mailpit)
    USE_LOCAL_MAIL: bool = True
    LOCAL_SMTP_HOST: str = "mailpit"
    LOCAL_SMTP_PORT: int = 1025

    MAIL_HASH_SALT: str = "default_salt"
    OTP_EXPIRY_MINUTES: int = 10
    RATE_LIMIT_HOURS: int = 168

    DOMAIN_NAME: str = "example.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
