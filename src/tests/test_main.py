from datetime import date
from ..main import app as my_app
from httpx import AsyncClient
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager


def create_student():
    return {
        "email": "new@student.com",
        "name": "John Doe",
        "date_of_birth": "2012-10-10",
        "university": "Stanford",
        "major": "Physics",
        "credits": 150,
        "gpa": 8.00,
        "password": "123",
    }


@pytest_asyncio.fixture(scope="module")
async def app():
    async with LifespanManager(my_app) as manager:
        yield manager.app


@pytest_asyncio.fixture(scope="module")
async def client(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        yield client


@pytest.mark.asyncio
async def test_home(client: AsyncClient):
    response = await client.get("/test")
    assert response.status_code == 200
    assert response.json() == "This is a test."


@pytest.mark.asyncio
async def test_student_pots(client: AsyncClient):
    student = create_student()
    response = await client.post("/students", json=student)
    print(response.json())
    assert response.status_code == 201
    print("OK")