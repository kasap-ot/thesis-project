from ..src.enums import UserType
from ..src.models import StudentCreate
from ..src.utils import generate_student
from .fixtures import session_fixture, client_fixture
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session
from httpx import Response


"""
[GENERAL]
Here we define pytest tests. All tests should be independent 
from each other i.e. they should be stateless. All tests use 
fixtures (similar to dependencies). Specifically we use a client 
fixture - for sending HTTP requests, and a session fixture - for 
sending database requests.
"""


"""
To reduce code duplication, we define student that will be created 
(inserted) in the database.
"""
TEST_CREATE_STUDENT = StudentCreate(
    email="john@doe.com",
    name="John Doe",
    password="john-secret",
    age=24,
    university="Some University",
    major="Electrical Engineering",
    credits=150,
    gpa=7.50,
)

""" To avoid hardcoding values and for code-readability. """
FAKE_ID = -1


def create_student_helper(client: TestClient) -> Response:
    """
    Helper function used when the goal is not to test the
    create-student functionality, but rather, other functionalities
    that depend on valid student creation via a POST request.
    For code readability and potential code-reusability.
    """
    return client.post("/students", json=TEST_CREATE_STUDENT.dict())


def login_for_token_helper(client: TestClient, user_type: UserType) -> Response:
    """
    Helper function. To reduce code duplication and increase readability.
    """
    return client.post(
        url=f"/token/{user_type.value}",
        headers={"Content Type": "application/json"},
        data={
            "username": TEST_CREATE_STUDENT.email,
            "password": TEST_CREATE_STUDENT.password,
        },
    )


def test_get_students_empty(client: TestClient):
    """
    Self-explanatory
    """
    response = client.get("/students")
    data = response.json()
    assert len(data) == 0
    assert response.status_code == status.HTTP_200_OK


def test_create_student(client: TestClient):
    """
    Self-explanatory
    """
    response = client.post("/students", json=TEST_CREATE_STUDENT.dict())
    data: dict = response.json()

    keys = data.keys()
    assert data["email"] == TEST_CREATE_STUDENT.email
    assert data["name"] == TEST_CREATE_STUDENT.name
    assert data["age"] == TEST_CREATE_STUDENT.age
    assert data["university"] == TEST_CREATE_STUDENT.university
    assert data["major"] == TEST_CREATE_STUDENT.major
    assert data["credits"] == TEST_CREATE_STUDENT.credits
    assert data["gpa"] == TEST_CREATE_STUDENT.gpa
    assert "hashed_password" not in keys
    assert "password" not in keys
    assert "id" in keys
    assert response.status_code == status.HTTP_201_CREATED


def test_get_students(client: TestClient, session: Session):
    """
    Self-explanatory
    """
    student_1 = generate_student()
    student_2 = generate_student()
    session.add(student_1)
    session.add(student_2)
    session.commit()
    session.refresh(student_1)
    session.refresh(student_2)

    response = client.get("/students")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        student_1.dict(exclude={"hashed_password"}), 
        student_2.dict(exclude={"hashed_password"}),
    ]


def test_create_invalid_student(client: TestClient):
    """
    Self-explanatory
    """
    new_student = {
        "email": "some@email.com",
        "name": "Some Name",
        "age": 30,
        "invalid_field": "invalid",
    }
    response = client.post("/students", json=new_student)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_one_student(client: TestClient, session: Session):
    """
    Self-explanatory
    """
    student = generate_student()
    session.add(student)
    session.commit()

    response = client.get(f"/students/{student.id}")
    data: dict = response.json()

    assert data["email"] == student.email
    assert data["name"] == student.name
    assert data["age"] == student.age
    assert data["id"] == student.id
    assert data["university"] == student.university
    assert data["major"] == student.major
    assert data["credits"] == student.credits
    assert data["gpa"] == student.gpa
    assert response.status_code == status.HTTP_200_OK


def test_read_fake_student(client: TestClient):
    """
    Self-explanatory
    """
    response = client.get(f"/students/{FAKE_ID}")
    data: dict = response.json()

    assert data == {"detail": "User not found"}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_token_student(client: TestClient):
    """
    Self-explanatory
    """
    create_student_helper(client)

    response = login_for_token_helper(client, UserType.STUDENT)
    data: dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert type(data["access_token"]) == type("some string")
    assert data["token_type"] == "bearer"


def test_get_invalid_token(client: TestClient):
    """
    Self-explanatory
    """
    response = client.post(
        url=f"/token/{UserType.STUDENT.value}",
        headers={"Content Type": "application/json"},
        data={"username": "fake@email.com", "password": "fake-secret"},
    )
    data: dict = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "User not found"


def update_student_helper(
    client: TestClient, student_id: int, token: str, updated_value: str
) -> Response:
    """
    Self-explanatory
    """
    return client.patch(
        f"/students/{student_id}",
        headers={"Authorization": "Bearer " + token},
        json={"name": updated_value},
    )


def test_update_student(client: TestClient):
    """
    Self-explanatory
    """
    response = create_student_helper(client)
    student_id = response.json()["id"]

    response = login_for_token_helper(client, UserType.STUDENT)
    data: dict = response.json()
    token: str = data["access_token"]

    updated_value = "Updated Value"
    response = update_student_helper(client, student_id, token, updated_value)
    data: dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["email"] == TEST_CREATE_STUDENT.email
    assert data["name"] == updated_value
    assert data["age"] == TEST_CREATE_STUDENT.age
    assert data["id"] == student_id
    assert data["university"] == TEST_CREATE_STUDENT.university
    assert data["major"] == TEST_CREATE_STUDENT.major
    assert data["credits"] == TEST_CREATE_STUDENT.credits
    assert data["gpa"] == TEST_CREATE_STUDENT.gpa


def test_update_student_invalid_token(client: TestClient):
    """
    Self-explanatory
    """
    response = create_student_helper(client)
    student_id = response.json()["id"]

    updated_value = "Updated Value"
    response = update_student_helper(client, student_id, "Invalid token", updated_value)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_update_student_not_owner(client: TestClient):
    """
    Self-explanatory
    """
    response = create_student_helper(client)
    student_id = response.json()["id"]
    other_student_id = student_id + 1

    updated_value = "Updated Value"
    response = login_for_token_helper(client, UserType.STUDENT)
    data: dict = response.json()
    token: str = data["access_token"]

    response = update_student_helper(client, other_student_id, token, updated_value)

    assert response.json() == {"detail": "Action not allowed"}
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_student(client: TestClient):
    """
    Self-explanatory
    """
    response = create_student_helper(client)
    student_id = response.json()["id"]

    response = login_for_token_helper(client, UserType.STUDENT)
    data: dict = response.json()
    token: str = data["access_token"]

    response = client.delete(
        f"/students/{student_id}",
        headers={"Authorization": "Bearer " + token},
    )
    data: dict = response.json()

    student_dict = TEST_CREATE_STUDENT.dict(exclude={"password"})
    student_dict["id"] = student_id
    assert data == student_dict
    assert response.status_code == status.HTTP_200_OK


def test_delete_student_invalid_token(client: TestClient):
    """
    Self-explanatory
    """
    response = create_student_helper(client)
    student_id = response.json()["id"]

    response = client.delete(
        f"/students/{student_id}",
        headers={"Authorization": "Bearer " + "INVALID TOKEN"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_delete_student_not_owner(client: TestClient):
    """
    Self-explanatory
    """
    response = create_student_helper(client)
    student_id = response.json()["id"]
    other_student_id = student_id + 1

    response = login_for_token_helper(client, UserType.STUDENT)
    data: dict = response.json()
    token: str = data["access_token"]

    response = client.delete(
        f"/students/{other_student_id}",
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Action not allowed"}


"""
A type of integration test. May not be necessary anymore.
"""

"""
def test_student_create_read_login_delete_read(client: TestClient):
    response = create_student_helper(client)
    student_id = response.json()["id"]

    response = client.get(f"/students/{student_id}")
    data: dict = response.json()

    assert response.status_code == 200
    assert data["name"] == TEST_CREATE_STUDENT.name

    response = login_for_token_helper(client, UserType.STUDENT)
    data: dict = response.json()
    token: str = data["access_token"]

    response = client.delete(
        f"/students/{student_id}",
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 200
    assert response.json()["name"] == TEST_CREATE_STUDENT.name
    
    response = client.get(f"/students/{student_id}")
    data: dict = response.json()

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
"""