import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.comparisons import router as comparisons_router
from app.config import settings, setup_logging
from app.config.logging import setup_logging
from app.database import InMemoryDatabase

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting up API")
    app.state.db = InMemoryDatabase()

    yield

    # Shutdown
    logger.info("Shutting down API")


app = FastAPI(lifespan=lifespan)

# Set all CORS enabled origins
if settings.CORS_ORGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(comparisons_router)
