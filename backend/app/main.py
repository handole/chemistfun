from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
import app.modules  # Register all models with Base.metadata

# Import all routers
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.classes.router import router as classes_router
from app.modules.content.router import router as content_router
from app.modules.assessment.router import router as assessment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist upon startup asynchronously in development
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="KimiFun API",
    version="1.0.0",
    description="API Backend untuk Laboratorium Maya & Platform Pembelajaran Kimia",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers under /api prefix
API_PREFIX = "/api"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(users_router, prefix=API_PREFIX)
app.include_router(classes_router, prefix=API_PREFIX)
app.include_router(content_router, prefix=API_PREFIX)
app.include_router(assessment_router, prefix=API_PREFIX)


@app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": "Welcome to KimiFun API",
        "status": "online",
        "docs_url": "/docs",
    }


@app.get("/api/health", tags=["Health"])
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "KimiFun-backend",
    }
