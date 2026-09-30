import os
from pathlib import Path

# Load .env file from backend directory if present
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k not in os.environ:
                    os.environ[k] = v

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/chemistfun_db",
)
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

# JWT Security Settings
SECRET_KEY: str = os.getenv(
    "SECRET_KEY",
    "chemistfun-insecure-development-secret-key-change-in-production-1234567890",
)
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24))  # 24 hours
)

# AI Service Settings
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "9router").lower()

# Option 1: 9router (OpenAI-compatible)
NINE_ROUTER_API_KEY: str = os.getenv("NINE_ROUTER_API_KEY", os.getenv("OPENAI_API_KEY", ""))
NINE_ROUTER_BASE_URL: str = os.getenv(
    "NINE_ROUTER_BASE_URL",
    os.getenv("OPENAI_BASE_URL", "https://api.9router.com/v1"),
).rstrip("/")
NINE_ROUTER_MODEL: str = os.getenv(
    "NINE_ROUTER_MODEL",
    os.getenv("OPENAI_MODEL", "ag/gemini-1.5-flash"),
)

# Option 2: Google Gemini Direct API
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


