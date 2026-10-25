

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.auth import failed_logins

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["API_KEY"] = "test-key"

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False)


@pytest.fixture
def client():
    failed_logins.reset()
    Base.metadata.create_all(engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app, headers={"X-API-Key": "test-key"})
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)