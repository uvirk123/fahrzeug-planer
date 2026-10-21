

from fastapi import FastAPI

from app.routes import health

app = FastAPI(
    title="Fahrzeug-Planer API",
    description="REST-API zur Planung von Fahrzeugprojekten und Meilensteinen",
    version="0.1.0",
)
app.include_router(health.router)