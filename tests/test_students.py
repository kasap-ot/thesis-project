from dataclasses import asdict
from httpx import AsyncClient
from fastapi import status
from .test_utils import (
    BASE_URL, 
    db_connection,
    insert_student,
    reset_database,
    create_token_header,
    student_token,
    create_student,
    StudentTest
)
import pytest


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
async def test_student_login(insert_student: StudentTest):   
    student = insert_student
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
async def test_student_profile(insert_student: StudentTest):
    student = insert_student
    async with AsyncClient(base_url=BASE_URL) as client:
        # get the token for acces
        token = await student_token(client, student)
        
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
async def test_student_update(insert_student: StudentTest):
    student = insert_student
    async with AsyncClient(base_url=BASE_URL) as client:
        # get the token for acces
        token = await student_token(client, student)

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
async def test_student_update_incorrect_field(insert_student: StudentTest):
    student = insert_student
    async with AsyncClient(base_url=BASE_URL) as client:
        # get the token for acces
        token = await student_token(client, student)

        # update a field in the student
        student.gpa = "This should be a float" # type: ignore

        # test the student put route
        response = await client.put(
            url=f"/students/{student.id}",
            headers=create_token_header(token),
            json=asdict(student)
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail"in response.json()

        # check if the field was properly updated
        response = await client.get(
            url=f"/students/profile/{student.id}",
            headers=create_token_header(token),
        )
        assert response.status_code == status.HTTP_200_OK
        assert student.major in response.text


@pytest.mark.asyncio
async def test_student_delete(insert_student: StudentTest):
    student = insert_student
    async with AsyncClient(base_url=BASE_URL) as client:
        # get the student's access token
        token = await student_token(client, student)
        
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

