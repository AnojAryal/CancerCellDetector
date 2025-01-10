from unittest.mock import Base
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from database import get_db
from main import app
from fastapi.testclient import TestClient

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

client = TestClient(app)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def setup():
    Base.metadata.create_all(bind=engine)


def teqardown():
    Base.metadata.drop_all(bind=engine)
