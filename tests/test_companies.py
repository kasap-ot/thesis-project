from ..src.enums import UserType
from ..src.models import CompanyCreate
from ..src.utils import generate_company
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
To reduce code duplication, we define a company that will be 
created (inserted) in the database.
"""
TEST_CREATE_COMPANY = CompanyCreate(
    email="company@llc.com",
    name="Company Inc.",
    password="company-secret",
    age=24,
    field="Mechanical Engineering",
    num_employees=100,
    year_founded=2000,
    website="some.website.com",
)

""" To avoid hardcoding values and for code-readability. """
FAKE_ID = -1


def create_company_helper(client: TestClient) -> Response:
    """
    Helper function used when the goal is not to test the
    create-company functionality, but rather, other functionalities
    that depend on valid company creation via a POST request.
    For code readability and potential code-reusability.
    """
    return client.post("/companies", json=TEST_CREATE_COMPANY.dict())


def login_for_token_helper(client: TestClient, user_type: UserType) -> Response:
    """
    Helper function. To reduce code duplication and increase readability.
    """
    return client.post(
        url=f"/token/{user_type.value}",
        headers={"Content Type": "application/json"},
        data={
            "username": TEST_CREATE_COMPANY.email,
            "password": TEST_CREATE_COMPANY.password,
        },
    )


def test_get_companies_empty(client: TestClient):
    """
    Self-explanatory
    """
    response = client.get("/companies")
    data = response.json()
    assert len(data) == 0
    assert response.status_code == status.HTTP_200_OK


def test_create_company(client: TestClient):
    """
    Self-explanatory
    """
    response = client.post("/companies", json=TEST_CREATE_COMPANY.dict())
    data: dict = response.json()

    keys = data.keys()
    assert data["email"] == TEST_CREATE_COMPANY.email
    assert data["name"] == TEST_CREATE_COMPANY.name
    assert data["age"] == TEST_CREATE_COMPANY.age
    assert data["field"] == TEST_CREATE_COMPANY.field
    assert data["num_employees"] == TEST_CREATE_COMPANY.num_employees
    assert data["year_founded"] == TEST_CREATE_COMPANY.year_founded
    assert data["website"] == TEST_CREATE_COMPANY.website
    assert "hashed_password" not in keys
    assert "password" not in keys
    assert "id" in keys
    assert response.status_code == status.HTTP_201_CREATED


def test_get_companies(client: TestClient, session: Session):
    """
    Self-explanatory
    """
    company_1 = generate_company()
    company_2 = generate_company()
    session.add(company_1)
    session.add(company_2)
    session.commit()
    session.refresh(company_1)
    session.refresh(company_2)

    response = client.get("/companies")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        company_1.dict(exclude={"hashed_password"}), 
        company_2.dict(exclude={"hashed_password"}),
    ]


def test_create_invalid_company(client: TestClient):
    """
    Self-explanatory
    """
    new_company = {
        "email": "some@email.com",
        "name": "Some Name",
        "age": 30,
        "invalid_field": "invalid",
    }
    response = client.post("/companies", json=new_company)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_one_company(client: TestClient, session: Session):
    """
    Self-explanatory
    """
    company = generate_company()
    session.add(company)
    session.commit()

    response = client.get(f"/companies/{company.id}")
    data: dict = response.json()

    assert data["email"] == company.email
    assert data["name"] == company.name
    assert data["age"] == company.age
    assert data["id"] == company.id
    assert data["field"] == company.field
    assert data["num_employees"] == company.num_employees
    assert data["year_founded"] == company.year_founded
    assert data["website"] == company.website
    assert response.status_code == status.HTTP_200_OK


def test_read_fake_company(client: TestClient):
    """
    Self-explanatory
    """
    response = client.get(f"/companies/{FAKE_ID}")
    data: dict = response.json()

    assert data == {"detail": "User not found"}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_token_company(client: TestClient):
    """
    Self-explanatory
    """
    create_company_helper(client)

    response = login_for_token_helper(client, UserType.COMPANY)
    data: dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert type(data["access_token"]) == type("some string")
    assert data["token_type"] == "bearer"


def test_get_invalid_token(client: TestClient):
    """
    Self-explanatory
    """
    response = client.post(
        url=f"/token/{UserType.COMPANY.value}",
        headers={"Content Type": "application/json"},
        data={"username": "fake@email.com", "password": "fake-secret"},
    )
    data: dict = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "User not found"


def update_company_helper(
    client: TestClient, company_id: int, token: str, updated_value: str
) -> Response:
    """
    Self-explanatory
    """
    return client.patch(
        f"/companies/{company_id}",
        headers={"Authorization": "Bearer " + token},
        json={"name": updated_value},
    )


def test_update_company(client: TestClient):
    """
    Self-explanatory
    """
    response = create_company_helper(client)
    company_id = response.json()["id"]

    response = login_for_token_helper(client, UserType.COMPANY)
    data: dict = response.json()
    token: str = data["access_token"]

    updated_value = "Updated Value"
    response = update_company_helper(client, company_id, token, updated_value)
    data: dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["email"] == TEST_CREATE_COMPANY.email
    assert data["name"] == updated_value
    assert data["age"] == TEST_CREATE_COMPANY.age
    assert data["id"] == company_id
    assert data["field"] == TEST_CREATE_COMPANY.field
    assert data["num_employees"] == TEST_CREATE_COMPANY.num_employees
    assert data["year_founded"] == TEST_CREATE_COMPANY.year_founded
    assert data["website"] == TEST_CREATE_COMPANY.website


def test_update_company_invalid_token(client: TestClient):
    """
    Self-explanatory
    """
    response = create_company_helper(client)
    company_id = response.json()["id"]

    updated_value = "Updated Value"
    response = update_company_helper(client, company_id, "Invalid token", updated_value)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_update_company_not_owner(client: TestClient):
    """
    Self-explanatory
    """
    response = create_company_helper(client)
    company_id = response.json()["id"]
    other_company_id = company_id + 1

    updated_value = "Updated Value"
    response = login_for_token_helper(client, UserType.COMPANY)
    data: dict = response.json()
    token: str = data["access_token"]

    response = update_company_helper(client, other_company_id, token, updated_value)

    assert response.json() == {"detail": "Action not allowed"}
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_company(client: TestClient):
    """
    Self-explanatory
    """
    response = create_company_helper(client)
    company_id = response.json()["id"]

    response = login_for_token_helper(client, UserType.COMPANY)
    data: dict = response.json()
    token: str = data["access_token"]

    response = client.delete(
        f"/companies/{company_id}",
        headers={"Authorization": "Bearer " + token},
    )
    data: dict = response.json()

    company_dict = TEST_CREATE_COMPANY.dict(exclude={"password"})
    company_dict["id"] = company_id
    assert data == company_dict
    assert response.status_code == status.HTTP_200_OK


def test_delete_company_invalid_token(client: TestClient):
    """
    Self-explanatory
    """
    response = create_company_helper(client)
    company_id = response.json()["id"]

    response = client.delete(
        f"/companies/{company_id}",
        headers={"Authorization": "Bearer " + "INVALID TOKEN"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_delete_company_not_owner(client: TestClient):
    """
    Self-explanatory
    """
    response = create_company_helper(client)
    company_id = response.json()["id"]
    other_company_id = company_id + 1

    response = login_for_token_helper(client, UserType.COMPANY)
    data: dict = response.json()
    token: str = data["access_token"]

    response = client.delete(
        f"/companies/{other_company_id}",
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Action not allowed"}


"""
A type of integration test. May not be necessary anymore.
"""

"""
def test_company_create_read_login_delete_read(client: TestClient):
    response = create_company_helper(client)
    company_id = response.json()["id"]

    response = client.get(f"/companies/{company_id}")
    data: dict = response.json()

    assert response.status_code == 200
    assert data["name"] == TEST_CREATE_COMPANY.name

    response = login_for_token_helper(client, UserType.COMPANY)
    data: dict = response.json()
    token: str = data["access_token"]

    response = client.delete(
        f"/companies/{company_id}",
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 200
    assert response.json()["name"] == TEST_CREATE_COMPANY.name
    
    response = client.get(f"/companies/{company_id}")
    data: dict = response.json()

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
"""