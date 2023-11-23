import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from httpx import Response
from models import User, UserCreate
from main import app
from database import get_session


"""
[GENERAL]
Here we define pytest tests. All tests should be independent 
from each other i.e. they should be stateless. All tests use 
fixtures (similar to dependencies). Specifically we use a client 
fixture - for sending HTTP requests, and a session fixture - for 
sending database requests.
"""


"""
To reduce code duplication, we define user that will be created 
(inserted) in the database.
"""
TEST_CREATE_USER = UserCreate(
    email="john@doe.com",
    name="John Doe",
    password="john-secret",
    age=24,
)

""" To avoid hardcoding values and for code-readability. """
FAKE_ID = -1


def create_user_helper(client: TestClient) -> Response:
    """
    Helper function used when the goal is not to test the
    create-user functionality, but rather, other functionalities
    that depend on valid user creation via a POST request.
    For code readability and potential code-reusability.
    """
    return client.post("/users", json=TEST_CREATE_USER.dict())


def login_for_token_helper(client: TestClient) -> Response:
    """
    Helper function. To reduce code duplication and increase readability.
    """
    return client.post(
        url="/token",
        headers={"Content Type": "application/json"},
        data={
            "username": TEST_CREATE_USER.email,
            "password": TEST_CREATE_USER.password,
        },
    )


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


def test_get_users_empty(client: TestClient):
    """
    Self-explanatory
    """
    response = client.get("/users")
    data = response.json()
    assert len(data) == 0
    assert response.status_code == status.HTTP_200_OK


def test_create_user(client: TestClient):
    """
    Self-explanatory
    """
    response = client.post("/users", json=TEST_CREATE_USER.dict())
    data: dict = response.json()

    keys = data.keys()
    assert data["email"] == TEST_CREATE_USER.email
    assert data["name"] == TEST_CREATE_USER.name
    assert data["age"] == TEST_CREATE_USER.age
    assert "hashed_password" not in keys
    assert "password" not in keys
    assert "id" in keys
    assert response.status_code == status.HTTP_201_CREATED


def test_get_users(client: TestClient, session: Session):
    """
    Self-explanatory
    """
    user_1 = User(
        email="first@email.com",
        name="First Name",
        age=20,
        hashed_password="first-secret",
    )
    user_2 = User(
        email="second@email.com",
        name="Second Name",
        age=26,
        hashed_password="second-secret",
    )
    session.add(user_1)
    session.add(user_2)
    session.commit()
    session.refresh(user_1)
    session.refresh(user_2)

    response = client.get("/users")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        user_1.dict(exclude={"hashed_password"}),
        user_2.dict(exclude={"hashed_password"}),
    ]


def test_create_invalid_user(client: TestClient):
    """
    Self-explanatory
    """
    new_user = {
        "email": "some@email.com",
        "name": "Some Name",
        "age": 30,
        "invalid_field": "invalid",
    }
    response = client.post("/users", json=new_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_one_user(client: TestClient, session: Session):
    """
    Self-explanatory
    """
    user = User(
        email="read@email.com", name="Some Name", age=42, hashed_password="some-hash"
    )
    session.add(user)
    session.commit()

    response = client.get(f"/users/{user.id}")
    data: dict = response.json()

    assert data["email"] == user.email
    assert data["name"] == user.name
    assert data["age"] == user.age
    assert data["id"] == user.id
    assert response.status_code == status.HTTP_200_OK


def test_read_fake_user(client: TestClient):
    """
    Self-explanatory
    """
    response = client.get(f"/users/{FAKE_ID}")
    data: dict = response.json()

    assert data == {"detail": "User not found"}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_token(client: TestClient):
    """
    Self-explanatory
    """
    create_user_helper(client)

    response = login_for_token_helper(client)
    data: dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert type(data["access_token"]) == type("some string")
    assert data["token_type"] == "bearer"


def test_get_invalid_token(client: TestClient):
    """
    Self-explanatory
    """
    response = client.post(
        url="/token",
        headers={"Content Type": "application/json"},
        data={"username": "fake@email.com", "password": "fake-secret"},
    )
    data: dict = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "User not found"


def update_user_helper(
    client: TestClient, user_id: int, token: str, updated_value: str
) -> Response:
    """
    Self-explanatory
    """
    return client.patch(
        f"/users/{user_id}",
        headers={"Authorization": "Bearer " + token},
        json={"name": updated_value},
    )


def test_update_user(client: TestClient):
    """
    Self-explanatory
    """
    response = create_user_helper(client)
    user_id = response.json()["id"]

    response = login_for_token_helper(client)
    data: dict = response.json()
    token: str = data["access_token"]

    updated_value = "Updated Value"
    response = update_user_helper(client, user_id, token, updated_value)
    data: dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["email"] == TEST_CREATE_USER.email
    assert data["name"] == updated_value
    assert data["age"] == TEST_CREATE_USER.age
    assert data["id"] == user_id


def test_update_user_invalid_token(client: TestClient):
    """
    Self-explanatory
    """
    response = create_user_helper(client)
    user_id = response.json()["id"]

    updated_value = "Updated Value"
    response = update_user_helper(client, user_id, "Invalid token", updated_value)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_update_user_not_owner(client: TestClient):
    """
    Self-explanatory
    """
    response = create_user_helper(client)
    user_id = response.json()["id"]
    other_user_id = user_id + 1

    updated_value = "Updated Value"
    response = login_for_token_helper(client)
    data: dict = response.json()
    token: str = data["access_token"]

    response = update_user_helper(client, other_user_id, token, updated_value)

    assert response.json() == {"detail": "Action not allowed"}
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_user(client: TestClient):
    """
    Self-explanatory
    """
    response = create_user_helper(client)
    user_id = response.json()["id"]

    response = login_for_token_helper(client)
    data: dict = response.json()
    token: str = data["access_token"]

    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": "Bearer " + token},
    )
    data: dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "email": TEST_CREATE_USER.email,
        "name": TEST_CREATE_USER.name,
        "age": TEST_CREATE_USER.age,
        "id": user_id,
    }


def test_delete_user_invalid_token(client: TestClient):
    """
    Self-explanatory
    """
    response = create_user_helper(client)
    user_id = response.json()["id"]

    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": "Bearer " + "INVALID TOKEN"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_delete_user_not_owner(client: TestClient):
    """
    Self-explanatory
    """
    response = create_user_helper(client)
    user_id = response.json()["id"]
    other_user_id = user_id + 1

    response = login_for_token_helper(client)
    data: dict = response.json()
    token: str = data["access_token"]

    response = client.delete(
        f"/users/{other_user_id}",
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Action not allowed"}
