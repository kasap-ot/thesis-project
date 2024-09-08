import psycopg as pg
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


async def get_company_token(client: AsyncClient, company: CompanyTest) -> dict:
    response = await client.post(
        url="/token?user_type_param=company",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": company.email,
            "password": company.password,
    })
    token = response.json()
    return token


@pytest.fixture(scope="function")
def insert_company_in_db(db_connection: pg.Connection) -> CompanyTest:
    company = create_company()
    db_connection.execute(
        "INSERT INTO companies "
        "(id, email, hashed_password, name, field, num_employees, year_founded, website) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        params=[
            company.id,
            company.email,
            company.hashed_password,
            company.name,
            company.field,
            company.num_employees,
            company.year_founded,
            company.website,
    ])
    db_connection.commit()
    return company


@pytest.mark.asyncio
async def test_company_register():
    company = create_company()
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(url="/companies", json=asdict(company))
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == None


@pytest.mark.asyncio
async def test_company_register_error():
    company = create_company()
    company_dict = asdict(company)
    company_dict["num_employees"] = "This should be a string."
    async with AsyncClient(base_url=BASE_URL) as client:
        resposne = await client.post(url="/companies", json=company_dict)
        assert resposne.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert isinstance(resposne.json(), dict)
    


@pytest.mark.asyncio
async def test_compeny_log_in(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        # test user login
        response = await client.post(
            url="/token?user_type_param=company",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "username": company.email,
                "password": company.password
            }
        )
        token = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in token
        assert token["token_type"] == "Bearer"

        # test view students' home page
        response = await client.get(
            url="/companies-home",
            headers={"Authorization": f"Bearer {token['access_token']}"})
        
        # test that we have an HTML template response
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert "</div>" in response.text


@pytest.mark.asyncio
async def test_company_get(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        token = await get_company_token(client, company)
        response = await client.get(
            url=f"/companies/{company.id}", 
            headers=create_token_header(token)
        )
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert "</div>" in response.text
        assert company.email in response.text
        assert company.website in response.text


@pytest.mark.asyncio
async def test_company_get_unauthorized(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get(url=f"/companies/{company.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert isinstance(response.json(), dict)
        assert "detail" in response.json()


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