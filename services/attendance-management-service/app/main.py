"""
FastAPI Application Entry Point.
Main application file with minimal configuration - delegates to modular components.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.logging import get_logger
from app.api.routes.employees import router as employees_router
from app.api.routes.auth import router as auth_router
from app.api.routes.attendance import router as attendance_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting application...")
    logger.info("Creating database and tables...")
    create_db_and_tables()
    logger.info("Database and tables created successfully")
    
    # Start Kafka producer (Optional - for async event publishing)
    if settings.KAFKA_ENABLE_PRODUCER:
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
            
            from shared.kafka import get_producer
            
            logger.info("Initializing Kafka producer...")
            await get_producer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id=settings.KAFKA_CLIENT_ID
            )
            logger.info(f"✅ Kafka producer started (topic: {settings.KAFKA_ATTENDANCE_TOPIC})")
        except Exception as e:
            logger.error(f"❌ Failed to start Kafka producer: {e}")
            logger.warning("Continuing without Kafka producer - HTTP endpoints still available")
    else:
        logger.info("Kafka producer disabled (KAFKA_ENABLE_PRODUCER=False)")
    
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Application shutting down...")
    
    # Stop Kafka producer
    if settings.KAFKA_ENABLE_PRODUCER:
        try:
            from shared.kafka import close_producer
            await close_producer()
            logger.info("✅ Kafka producer stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping Kafka producer: {e}")




# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(employees_router, prefix="/api/v1")
app.include_router(attendance_router, prefix="/api/v1")


# Health check endpoint
@app.get("/", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    Returns service status and basic information.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["health"])
async def detailed_health_check():
    """
    Detailed health check endpoint.
    Can be extended to include database connectivity checks, etc.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": settings.DB_NAME,
    }
# test change
