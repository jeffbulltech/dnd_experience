from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Must be set BEFORE app imports so get_settings() sees testing mode
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-1234567890")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings

# Clear cached settings so testing env vars take effect
get_settings.cache_clear()

from app.database import Base, get_db
from app.main import app
from app import models  # noqa: F401  # ensure models are imported for metadata


@pytest.fixture()
def db_session():
    """Create an in-memory SQLite database session for testing."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    # Enable foreign key enforcement so CASCADE works like PostgreSQL
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    TestingSession = sessionmaker(bind=connection, autoflush=False, autocommit=False, future=True)
    session = TestingSession()
    
    try:
        yield session
    finally:
        transaction.rollback()
        connection.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user(db_session):
    """Create a test user for authentication tests."""
    from app.services import auth_service
    from app.schemas.auth import UserCreate
    
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        display_name="Test User"
    )
    return auth_service.create_user(db_session, user_data)


@pytest.fixture()
def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    # Login to get token
    response = client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    
    # Set default headers
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


@pytest.fixture()
def mock_ollama_client():
    """Mock Ollama client for testing AI GM responses."""
    with patch("app.services.ollama_service._get_client") as mock:
        mock_client = Mock()
        mock_client.chat.return_value = {
            "message": {"content": "Test GM response"},
            "model": "mistral",
            "prompt_eval_count": 100,
            "eval_count": 50
        }
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture()
def mock_chroma_db():
    """Mock ChromaDB vector store for RAG testing."""
    with patch("app.services.rag_service._get_vector_store") as mock:
        mock_store = Mock()
        # Create a mock document object
        mock_doc = Mock()
        mock_doc.page_content = "Test rule content from SRD"
        mock_doc.metadata = {"source": "SRD - Combat Rules"}
        
        mock_store.similarity_search_with_score.return_value = [
            (mock_doc, 0.95)
        ]
        mock.return_value = mock_store
        yield mock_store
