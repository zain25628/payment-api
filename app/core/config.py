import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Payment Gateway API"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/payment_gateway")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME")

settings = Settings()
