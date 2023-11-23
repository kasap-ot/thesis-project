import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from models import User, UserCreate
from main import app
from database import get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        url="sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_get_users_empty(client: TestClient):
    response = client.get("/users")
    data = response.json()
    assert len(data) == 0
    assert response.status_code == status.HTTP_200_OK


def test_create_user(client: TestClient):    
    new_user = {
        "email": "some@email.com",
        "name": "John Doe",
        "age": 30,
        "password": "john-secret",
    }
    
    response = client.post("/users", json = new_user)
    data: dict = response.json()

    assert len(new_user.keys()) == len(data.keys())
    assert data["email"] == new_user["email"]
    assert data["name"] == new_user["name"]
    assert data["age"] == new_user["age"]
    assert data["id"] == 1
    assert response.status_code == status.HTTP_201_CREATED
    

def test_read_one_user(client: TestClient, session: Session):
    new_user = User(
        email="some@email.com",
        name="joker",
        age=50,
        hashed_password="some-hash",
    )
    session.add(new_user)
    session.commit()

    response = client.get(f"/users/{new_user.id}")
    data: dict = response.json()

    assert data["email"] == new_user.email
    assert data["name"] == new_user.name
    assert data["age"] == new_user.age
    assert data["id"] == new_user.id
    assert response.status_code == status.HTTP_200_OK


def test_read_fake_user(client: TestClient):
    fake_id = 5

    response = client.get(f"/users/{fake_id}")
    data: dict = response.json()

    assert data == {"detail": "User not found"}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_token(client: TestClient, session: Session):
    new_user = UserCreate(
        email="john@doe.com",
        name="John Doe",
        age=24,
        password="john-secret",
    )
    response = client.post("/users", json=new_user.dict())
    assert response.status_code == status.HTTP_201_CREATED
    response = client.post(
        url = "/token", 
        headers = {"Content Type": "application/json"},
        data = {
            "username": "john@doe.com", 
            "password": "john-secret"
        }
    )
    data: dict = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert type(data["access_token"]) == type("some string")
    assert data["token_type"] == "bearer"


def test_get_invalid_token(client: TestClient, session: Session):
    response = client.post(
        url = "/token", 
        headers = {"Content Type": "application/json"},
        data = {
            "username": "fake@email.com", 
            "password": "fake-secret"
        }
    )
    data: dict = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "User not found"

# delete one user - needs authentication

# read all users - not empty