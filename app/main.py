

import logging
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request

from app import models  # noqa: F401
from app.auth import require_api_key
from app.config import settings
from app.database import Base, engine
from app.logging_config import setup_logging
from app.routes import health, milestones, projects

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("application started")
    yield


app = FastAPI(
    title="Fahrzeug-Planer API",
    description="REST-API zur Planung von Fahrzeugprojekten und Meilensteinen",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 1)

    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


protected = [Depends(require_api_key)]

app.include_router(health.router)
app.include_router(projects.router, dependencies=protected)
app.include_router(milestones.router, dependencies=protected)