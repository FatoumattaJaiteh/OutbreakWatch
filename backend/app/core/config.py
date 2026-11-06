import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Ebola Traveller Screening & QR Code Verification System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://localhost:8000,http://127.0.0.1:5500,http://localhost:5500,http://localhost:8080,http://127.0.0.1:8000"
        ).split(",")
        if origin.strip()
    ]
    
    # Supabase credentials
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://kkhnjblywdbmtwbubqlm.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "sb_publishable_LMWqeCqmjvlhme9IDZdjqg_tgmeBY_D")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Security
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "admin-secret-dev-key")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ebola-screening-the-gambia-secret-key-2026")


settings = Settings()
