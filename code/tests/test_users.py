import pytest
import requests
from http import HTTPStatus


BASE_URL = "http://localhost:8000"


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
    restart_url = f"{BASE_URL}/restart-database"
    requests.delete(url=restart_url)


def test_student(reset_database):
    # create the student
    student = create_student()
    student_url = f"{BASE_URL}/students"
    response = requests.post(url=student_url, json=student)
    assert response.status_code == HTTPStatus.CREATED.value

    # login to get the user JWT token
    user_type = "student"
    login_body = f"username={student['email']}&password={student['password']}"
    login_url = f"{BASE_URL}/token?user_type_param={user_type}"
    login_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(
        url=login_url,
        headers=login_headers,
        data=login_body,
    )
    token_data = response.json()
    assert response.status_code == HTTPStatus.OK.value
    assert token_data["token_type"] == "bearer"


def test_student_2(reset_database):
    # create the student
    student = create_student()
    student_url = f"{BASE_URL}/students"
    response = requests.post(url=student_url, json=student)
    assert response.status_code == HTTPStatus.CREATED.value

    # login to get the user JWT token
    user_type = "student"
    login_body = f"username={student['email']}&password={student['password']}"
    login_url = f"{BASE_URL}/token?user_type_param={user_type}"
    login_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(
        url=login_url,
        headers=login_headers,
        data=login_body,
    )
    token_data = response.json()
    assert response.status_code == HTTPStatus.OK.value
    assert token_data["token_type"] == "bearer"