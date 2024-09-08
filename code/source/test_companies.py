from httpx import AsyncClient
from .utils import pwd_context
from dataclasses import asdict, dataclass
from .test_utils import BASE_URL, create_token_header, delete_db_data, db_connection, reset_database
from fastapi import status
import pytest


@dataclass
class CompanyTest:
    id: int
    email: str
    password: str
    hashed_password: str
    name: str
    field: str
    num_employees: int
    year_founded: int
    website: str


def create_company() -> CompanyTest:
    return CompanyTest(
        id=1,
        email="company@test.com",
        password="company-password",
        hashed_password=pwd_context.hash("company-password"),
        name="Test LLC",
        field="Test Field",
        num_employees=230,
        year_founded=1999,
        website="www.test-llc.com",
    )


@pytest.mark.asyncio
async def test_company_register():
    company = create_company()
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(url="/companies", json=asdict(company))
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == None


@pytest.mark.asyncio
async def test_compeny_log_in():
    ...


@pytest.mark.asyncio
async def test_company_post():
    ...


@pytest.mark.asyncio
async def test_company_get():
    ...


@pytest.mark.asyncio
async def test_company_offers_get():
    ...


@pytest.mark.asyncio
async def test_company_edit_get():
    ...


@pytest.mark.asyncio
async def test_company_path():
    ...


@pytest.mark.asyncio
async def test_company_delete():
    ...


@pytest.mark.asyncio
async def test_company_home_get():
    ...