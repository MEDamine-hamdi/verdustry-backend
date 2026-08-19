from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    TURNSTILE_SECRET_KEY: str
    BREVO_API_KEY: str
    FRONTEND_URL: str = "https://verdustry-services.vercel.app/"
    GOOGLE_CLIENT_ID: str

    # --- OpenLCA (IPC) ---
    OPENLCA_IPC_HOST: str = "localhost"
    OPENLCA_IPC_PORT: int = 8091

    # --- Odoo (XML-RPC) ---
    ODOO_URL: str
    ODOO_DB: str
    ODOO_USERNAME: str
    ODOO_API_KEY: str
    # --- RAG    ---
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    class Config:
        env_file = ".env"

settings = Settings()