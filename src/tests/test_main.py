from http import HTTPStatus
import pytest
from ..main import app
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_app_is_live():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get("/test")
    assert response.status_code == HTTPStatus.OK.value
    assert response.json() == "This is a test."


# @pytest.mark.asyncio
# async def test_student_post():
#     student = {
#         "email": "student@email.com",
#         "name": "John Doe",
#         "date_of_birth": "2000-01-01",
#         "university": "Stanford",
#         "major": "Computer Science",
#         "credits": 150,
#         "gpa": 8.00,
#         "password": "some-password",
#     }
#     async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
#         response = await ac.post("/students", json=student)
#     assert response.status_code == HTTPStatus.CREATED.value
#     assert response.json() == None