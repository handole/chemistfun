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

# Database Configuration (Mandatory from .env)
DATABASE_URL: str = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment or .env file.")

# Build AsyncPG connection string from DATABASE_URL
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL

ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

# JWT Security Settings (Mandatory from .env)
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in environment or .env file.")

ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# CORS Configuration
# 1. Explicit list (comma-separated): e.g. http://localhost:5173,https://my-node.ts.net,http://100.x.y.z:5173
CORS_ORIGINS_RAW: str = os.getenv("CORS_ORIGINS", "")
if CORS_ORIGINS_RAW.strip():
    CORS_ORIGINS = [orig.strip() for orig in CORS_ORIGINS_RAW.split(",") if orig.strip()]
else:
    CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

# 2. Regex pattern for Tailscale Funnel (https://*.ts.net) and Tailscale CGNAT IP (100.64.0.0/10)
# Default regex matches all Tailscale Funnel domains (*.ts.net) and Tailscale IP (100.x.x.x)
CORS_ORIGIN_REGEX: str = os.getenv(
    "CORS_ORIGIN_REGEX",
    r"^https://.*\.ts\.net(:\d+)?$|^http://100\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$"
)

# AI Service Settings (All purely read from .env)
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "").lower()

# Option 1: 9router (OpenAI-compatible)
NINE_ROUTER_API_KEY: str = os.getenv("NINE_ROUTER_API_KEY", os.getenv("OPENAI_API_KEY", ""))
NINE_ROUTER_BASE_URL: str = os.getenv("NINE_ROUTER_BASE_URL", os.getenv("OPENAI_BASE_URL", "")).rstrip("/")
NINE_ROUTER_MODEL: str = os.getenv("NINE_ROUTER_MODEL", os.getenv("OPENAI_MODEL", ""))

# Option 2: Google Gemini Direct API
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "")
