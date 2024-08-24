import pytest
import requests
from http import HTTPStatus


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


@pytest.fixture()
def reset_database():
    restart_url = "http://localhost:8000/restart-database"
    requests.delete(url=restart_url)


def test_student_post(reset_database):
    student_url = "http://localhost:8000/students"
    response = requests.post(url=student_url, json=create_student())
    assert response.status_code == HTTPStatus.CREATED.value


def test_student_put(reset_database):
    