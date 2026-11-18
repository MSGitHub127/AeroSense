"""Pytest fixtures and test environment configuration for AeroSense."""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Enforce mock mode and test encryption key for all test suites
os.environ["AEROSENSE_LLM_PROVIDER"] = "mock"
os.environ["AEROSENSE_FERNET_KEY"] = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
os.environ["AEROSENSE_DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.deps import get_db_session
from app.main import app
from app.models import CommuteMode, CookingFuel, FamilyProfileRequest, HomeType


@pytest.fixture(scope="session")
def test_db_engine():
    """In-memory SQLite database engine shared across session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db_engine):
    """Transactional session fixture rolling back after each test."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session = session_factory()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session):
    """FastAPI TestClient with overridden database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_profile_payload() -> FamilyProfileRequest:
    """Fixture providing a standard multi-vulnerability household payload."""
    return FamilyProfileRequest(
        household_name="Sharma Household",
        location_city="Delhi",
        home_type=HomeType.APARTMENT,
        cooking_fuel=CookingFuel.GAS,
        commute_mode=CommuteMode.CAR_SOLO,
        has_hepa_purifier=False,
        vulnerable_members=["infant_daughter", "asthmatic_father"],
        baseline_aqi=340,
    )
