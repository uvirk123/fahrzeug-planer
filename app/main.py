from fastapi import FastAPI

app = FastAPI(
    title="Fahrzeug-Planer API",
    description="REST-API zur Planung von Fahrzeugprojekten und Meilensteinen",
    version="0.1.0",
)


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    """Prüft, ob die Anwendung läuft."""
    return {"status": "ok"}
