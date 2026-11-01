import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["AUTH_SECRET"] = "test-secret-that-is-long-enough"

from app.database import Base, get_db
from app.main import app
from app.models import DetectionRule


@pytest.fixture
def client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with factory() as db:
        db.add(DetectionRule(id="AUTH-001", name="Multiple failed logins", description="test", severity="medium", enabled=True, time_window_seconds=600))
        db.commit()

    def override():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    yield client_factory(app)
    app.dependency_overrides.clear()


def client_factory(app):
    from fastapi.testclient import TestClient
    return TestClient(app)
