from dataclasses import dataclass, asdict
from httpx import AsyncClient
from .utils import pwd_context
from fastapi import status
from .database import get_connection_string
from .test_utils import BASE_URL, delete_db_data, db_connection, reset_database, create_token_header
import psycopg as pg
import pytest


@dataclass
class StudentTest:
    id: int
    email: str
    name: str
    date_of_birth: str
    university: str
    major: str
    credits: int
    gpa: float
    region_id: int
    password: str
    hashed_password: str


def create_student() -> StudentTest:
    return StudentTest(
        id = 1,
        email = "student@test.com",
        name = "Test Name",
        date_of_birth = "2000-01-01",
        university = "Test University",
        major = "Test Major",
        credits = 150,
        gpa = 8.50,
        region_id = 0,
        password = "Test Password",
        hashed_password = pwd_context.hash("Test Password"),
    )


async def get_student_token(client: AsyncClient, student: StudentTest) -> dict:
    response = await client.post(
        url="/token?user_type_param=student",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": student.email,
            "password": student.password,
    })
    token = response.json()
    return token


@pytest.fixture(scope="function")
def insert_student_in_db(db_connection: pg.Connection) -> StudentTest:
    student = create_student()
    db_connection.execute(
        "INSERT INTO students "
        "(id, email, hashed_password, name, university, major, credits, gpa, date_of_birth, region_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
        params=[
            student.id,
            student.email,
            student.hashed_password,
            student.name,
            student.university,
            student.major,
            student.credits,
            student.gpa,
            student.date_of_birth,
            student.region_id,
    ])
    db_connection.commit()
    return student


@pytest.mark.asyncio
async def test_test_route():
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/test")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "This is a test message."}


@pytest.mark.asyncio
async def test_student_registration():
    student = create_student()
    async with AsyncClient(base_url=BASE_URL) as client:
        # test user registration
        response = await client.post("/students", json=asdict(student))
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == None


@pytest.mark.asyncio
async def test_student_registration_error():
    student = create_student()
    student_dict = asdict(student)
    student_dict["credits"] = "This should be an integer"
    async with AsyncClient(base_url=BASE_URL) as client:
        # test user registration with incorrect parameter
        response = await client.post("/students", json=student_dict)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert isinstance(response.json(), dict)


@pytest.mark.asyncio
async def test_student_login(insert_student_in_db: StudentTest):   
    student = insert_student_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        # test user login
        response = await client.post(
            url="/token?user_type_param=student",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "username": student.email,
                "password": student.password
            }
        )
        token = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in token
        assert token["token_type"] == "Bearer"

        # test view students' home page
        response = await client.get(
            url="/students-home",
            headers={"Authorization": f"Bearer {token['access_token']}"})
        
        # test that we have an HTML template response
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert "</div>" in response.text


@pytest.mark.asyncio
async def test_student_profile(insert_student_in_db: StudentTest):
    student = insert_student_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        # get the token for acces
        token = await get_student_token(client, student)
        
        # test the student profile route
        response = await client.get(
            url=f"/students/profile/{student.id}",
            headers={"Authorization": f"Bearer {token['access_token']}"})
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert "</div>" in response.text

        # test the edit-student-profile route
        response = await client.get(
            url=f"/students/profile/{student.id}/edit",
            headers=create_token_header(token),
        )
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert "</div>" in response.text
        assert student.date_of_birth in response.text
        assert student.university in response.text


@pytest.mark.asyncio
async def test_student_update(insert_student_in_db: StudentTest):
    student = insert_student_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        # get the token for acces
        token = await get_student_token(client, student)

        # update a field in the student
        student.major = "__New__Updated__Major__"

        # test the student put route
        response = await client.put(
            url=f"/students/{student.id}",
            headers=create_token_header(token),
            json=asdict(student)
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == None

        # check if the field was properly updated
        response = await client.get(
            url=f"/students/profile/{student.id}",
            headers=create_token_header(token),
        )
        assert response.status_code == status.HTTP_200_OK
        assert student.major in response.text


@pytest.mark.asyncio
async def test_student_delete(insert_student_in_db: StudentTest):
    student = insert_student_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        # get the student's access token
        token = await get_student_token(client, student)
        
        # check the student-delete route
        response = await client.delete(
            url=f"/students/{student.id}",
            headers=create_token_header(token),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == None

        # test if the student no longer exists
        response = await client.get(
            url=f"/students/profile/{student.id}",
            headers=create_token_header(token),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}

