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
    # create a student (register)
    # call the /token endpoing
    # store the token in a variable
    # call the PUT enpoint for /students
    # pass in the token in the HTTP header
    # update the student
    # check if the status code is correct
    # check if the updated students is mathing
    ...


def test_student_delete(reset_database):
    ...


def test_