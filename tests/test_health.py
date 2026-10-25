from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app, docs_settings

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_redirects_to_docs():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_docs_are_available_by_default():
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_docs_can_be_disabled():
    app_without_docs = FastAPI(**docs_settings(False))
    test_client = TestClient(app_without_docs)

    assert test_client.get("/docs").status_code == 404
    assert test_client.get("/redoc").status_code == 404
    assert test_client.get("/openapi.json").status_code == 404