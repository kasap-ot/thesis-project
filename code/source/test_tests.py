from httpx import AsyncClient
from datetime import date
from fastapi import status
from .schemas import StudentCreate
from .database import get_connection_string
import psycopg as pg
import pytest


url = "http://127.0.0.1:8000"


def create_student() -> dict:
    return {
        'email': "student@test.com",
        'name': "Test Name",
        'date_of_birth': "2000-01-01",
        'university': "Test University",
        'major': "Test Major",
        'credits': 150,
        'gpa': 8.50,
        'region_id': 0,
        'password': "Test Password",
    }

def delete_rows_in_db(db_connection: pg.Connection):
    db_connection.execute("DELETE FROM applications;")
    db_connection.execute("DELETE FROM experiences;")
    db_connection.execute("DELETE FROM offers;")
    db_connection.execute("DELETE FROM students;")
    db_connection.execute("DELETE FROM companies;")
    db_connection.commit()


@pytest.fixture(scope="module")
def db_connection():
    db_string = get_connection_string()
    with pg.connect(db_string) as db_connection:
        yield db_connection
        delete_rows_in_db(db_connection)


@pytest.fixture(scope="function")
def reset_database(db_connection: pg.Connection):
    delete_rows_in_db(db_connection)


@pytest.mark.asyncio
async def test_test(reset_database):
    async with AsyncClient(base_url=url) as client:
        response = await client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "This is a test message."}


@pytest.mark.asyncio
async def test_student(reset_database):
    student = create_student()
    async with AsyncClient(base_url=url) as client:
        # user registration
        response = await client.post("/students", json=student)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == None

        # user login
        response = await client.post(
            url="/token?user_type_param=student",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "username": student["email"],
                "password": student["password"],
            }
        )
        token = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in token
        assert token["token_type"] == "Bearer"

        # view offers
        ...

        # view profile
        ...

        # edit profile
        ...

        # view one offer
        ...

        # apply for the offer
        ...