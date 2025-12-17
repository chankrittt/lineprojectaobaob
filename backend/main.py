from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import redis

from app.core.config import settings
from app.core.database import engine, Base
from app.api.endpoints import auth, files, search, webhook, collections
from app.utils.rate_limiter import initialize_rate_limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Drive2 application...")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    # Initialize rate limiter with Redis
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        redis_client.ping()  # Test connection
        initialize_rate_limiter(redis_client)
        logger.info("Rate limiter initialized with Redis")
    except Exception as e:
        logger.warning(f"Failed to initialize rate limiter: {e}. Rate limiting disabled.")

    yield

    # Shutdown
    logger.info("Shutting down Drive2 application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook.router, prefix=f"{settings.API_V1_PREFIX}/webhook", tags=["webhook"])
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(files.router, prefix=f"{settings.API_V1_PREFIX}/files", tags=["files"])
app.include_router(search.router, prefix=f"{settings.API_V1_PREFIX}/search", tags=["search"])
app.include_router(collections.router, prefix=f"{settings.API_V1_PREFIX}/collections", tags=["collections"])


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
