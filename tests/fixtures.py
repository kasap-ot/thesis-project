import pytest
from sqlmodel import SQLModel, Session, create_engine, StaticPool
from ..src.main import app
from ..src.database import get_session
from fastapi.testclient import TestClient


@pytest.fixture(name="session")
def session_fixture():
    """
    A fixture (dependency) used by tests for DB communication.
    """
    engine = create_engine(
        url="sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    A fixture (dependency) used by tests for sending HTTP requests.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()