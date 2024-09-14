import psycopg as pg
from httpx import AsyncClient
from .enums import Region
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


@dataclass
class OfferTest:
    id: int
    salary: int
    num_weeks: int
    field: str
    deadline: str
    requirements: str
    responsibilities: str
    company_id: int
    region_id: int


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


def create_offer(company_id: int, offer_id: int = 1) -> OfferTest:
    return OfferTest(
        id=offer_id,
        salary=2000,
        num_weeks=20,
        field="Test Field",
        deadline="2024-10-01",
        requirements="Test Requirements",
        responsibilities="Test Responsibilities",
        company_id=company_id,
        region_id=Region.GLOBAL.value,
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


@pytest.fixture(scope="function")
def insert_offers_in_db(db_connection: pg.Connection, insert_company_in_db: CompanyTest) -> dict:
    company = insert_company_in_db
    o1 = create_offer(company.id, 1)
    o2 = create_offer(company.id, 2)
    o3 = create_offer(company.id, 3)
    db_connection.execute(
        "INSERT INTO offers "
        "(id, salary, num_weeks, field, deadline, requirements, responsibilities, company_id, region_id) "
        "VALUES "
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s), "
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s), "
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        params=[
            o1.id, o1.salary, o1.num_weeks, o1.field, o1.deadline, o1.requirements, o1.responsibilities, o1.company_id, o1.region_id,
            o2.id, o2.salary, o2.num_weeks, o2.field, o2.deadline, o2.requirements, o2.responsibilities, o2.company_id, o2.region_id,
            o3.id, o3.salary, o3.num_weeks, o3.field, o3.deadline, o3.requirements, o3.responsibilities, o3.company_id, o3.region_id,
    ])
    db_connection.commit()
    return {"offers": [o1, o2, o3], "company": company}
    


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
async def test_company_offers_get(insert_offers_in_db: dict):
    offers: list[OfferTest] = insert_offers_in_db["offers"]
    company: CompanyTest = insert_offers_in_db["company"]
    first_offer = offers[0]
    async with AsyncClient(base_url=BASE_URL) as client:
        token = await get_company_token(client, company)
        response = await client.get(
            url=f"/companies/{first_offer.company_id}/offers",
            headers=create_token_header(token)
        )
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert "</div>" in response.text
        assert first_offer.field in response.text
        assert first_offer.deadline in response.text
        assert str(first_offer.num_weeks) in response.text


@pytest.mark.asyncio
async def test_company_offers_get_no_offers(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        token = await get_company_token(client, company)
        response = await client.get(
            url=f"/companies/{company.id}/offers",
            headers=create_token_header(token)
        )
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert "</div>" in response.text


@pytest.mark.asyncio
async def test_company_edit_get(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get(url=f"/companies/{company.id}/edit")
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert "</div>" in response.text
        assert company.website in response.text
        assert company.email in response.text



@pytest.mark.asyncio
async def test_company_edit_get_no_company():
    fake_company_id = 100
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get(url=f"/companies/{fake_company_id}/edit")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_company_patch(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    company.website = "www.updated-website.com"
    async with AsyncClient(base_url=BASE_URL) as client:
        token = await get_company_token(client, company)
        response = await client.put(
            url=f"/companies/{company.id}",
            headers=create_token_header(token),
            json=asdict(company),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == None


@pytest.mark.asyncio
async def test_company_patch_no_company():
    fake_company = create_company()
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.put(
            url=f"/companies/{fake_company.id}",
            json=asdict(fake_company),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_company_patch_incorrect_field(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    company.num_employees = "This should be an integer" # type: ignore
    async with AsyncClient(base_url=BASE_URL) as client:
        token = await get_company_token(client, company)
        response = await client.put(
            url=f"/companies/{company.id}",
            headers=create_token_header(token),
            json=asdict(company),
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_company_delete(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        token = await get_company_token(client, company)
        response = await client.delete(
            url=f"/companies/{company.id}",
            headers=create_token_header(token),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == None


@pytest.mark.asyncio
async def test_company_delete_no_company():
    fake_company = create_company()
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.delete(url=f"/companies/{fake_company.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_company_delete_unauthorized(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.delete(url=f"/companies/{company.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_company_home_get(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        token = await get_company_token(client, company)
        response = await client.get(
           url="/companies-home",
           headers=create_token_header(token)
        )
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert "</div>" in response.text


@pytest.mark.asyncio
async def test_company_home_get_unauthorized():
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get(
           url="/companies-home",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()