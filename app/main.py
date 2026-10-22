

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401
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
app.include_router(health.router)
app.include_router(projects.router)
app.include_router(milestones.router)