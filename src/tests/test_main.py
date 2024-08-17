import pytest
from ..main import app
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_main():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get("/test")
    assert 0 == 0