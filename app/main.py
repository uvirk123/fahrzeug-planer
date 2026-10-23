

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app import models  # noqa: F401
from app.auth import require_api_key
from app.database import Base, engine
from app.routes import health, milestones, projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Fahrzeug-Planer API",
    description="REST-API zur Planung von Fahrzeugprojekten und Meilensteinen",
    version="0.1.0",
    lifespan=lifespan,
)

protected = [Depends(require_api_key)]

app.include_router(health.router)
app.include_router(projects.router, dependencies=protected)
app.include_router(milestones.router, dependencies=protected)