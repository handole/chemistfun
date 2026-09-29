import os

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

