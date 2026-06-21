import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))
    
    FITBARK_CLIENT_ID: str = os.getenv("FITBARK_CLIENT_ID", "mock_id")
    FITBARK_CLIENT_SECRET: str = os.getenv("FITBARK_CLIENT_SECRET", "mock_secret")
    FITBARK_REDIRECT_URI: str = os.getenv("FITBARK_REDIRECT_URI", "http://localhost:8000/api/v1/fitbark/callback")

    IAP_VALIDATION_MODE: str = os.getenv("IAP_VALIDATION_MODE", "mock")
    APPLE_SHARED_SECRET: str = os.getenv("APPLE_SHARED_SECRET", "")
    GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")

settings = Settings()
