import pytest
import requests
from http import HTTPStatus


BASE_URL = "http://localhost:8000/"


def create_student() -> dict:
    return {
        "email": "new@student.com",
        "name": "John Doe",
        "date_of_birth": "2012-10-01",
        "university": "Stanford",
        "major": "Physics",
        "credits": 150,
        "gpa": 8.00,
        "password": "fake password",
    }


@pytest.fixture(scope="module")
def reset_database():
    ...


def test_tmp():
    url = "http://localhost:8000/students"
    response = requests.post(
        url=url,
        json=create_student(),
    )
    assert response.status_code == HTTPStatus.CREATED.value