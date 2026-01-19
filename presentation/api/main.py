import logging
import signal
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from infrastructure.config import settings
from presentation.api.routers import decks, cards, study, users, import_router, tts_router

import os
log_handlers = [logging.StreamHandler()]
if settings.log_file:
    os.makedirs(os.path.dirname(settings.log_file) if os.path.dirname(settings.log_file) else ".", exist_ok=True)
    log_handlers.append(logging.FileHandler(settings.log_file))

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=log_handlers
)
logger = logging.getLogger(__name__)

# Переменная для graceful shutdown
shutdown_event = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    try:
        from infrastructure.database.database import init_db
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    try:
        from infrastructure.services.cache_service import cache_service
        await cache_service.connect()
        logger.info("Redis cache connected")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")
    
    yield

    logger.info(f"Shutting down {settings.app_name}")

    try:
        from infrastructure.services.cache_service import cache_service
        await cache_service.disconnect()
        logger.info("Redis cache disconnected")
    except Exception:
        pass


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Quizlet-like learning application with FSRS algorithm",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        openapi_schema.setdefault("components", {})
        security_schemes = openapi_schema["components"].setdefault("securitySchemes", {})
        security_schemes["bearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключение роутеров
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(decks.router, prefix="/api/v1/decks", tags=["Decks"])
    app.include_router(cards.router, prefix="/api/v1/cards", tags=["Cards"])
    app.include_router(study.router, prefix="/api/v1/study", tags=["Study"])
    app.include_router(import_router.router, prefix="/api/v1/import", tags=["Import"])
    app.include_router(tts_router.router, prefix="/api/v1/tts", tags=["Text-to-Speech"])

    @app.get("/")
    async def root():
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs"
        }

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    return app


app = create_app()

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "presentation.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
