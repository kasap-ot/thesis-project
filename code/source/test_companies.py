from httpx import AsyncClient
from dataclasses import asdict
from .test_utils import (
    BASE_URL, 
    create_token_header, 
    get_company_token, 
    create_company, 
    CompanyTest, 
    OfferTest,
    insert_company_in_db,
    insert_offers_in_db,
    db_connection,
    reset_database,
)
from fastapi import status
import pytest
    


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
        # update the field
        response = await client.put(
            url=f"/companies/{company.id}",
            headers=create_token_header(token),
            json=asdict(company),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == None

        # check if the field was actually updated
        response = await client.get(f"/companies/{company.id}/edit")
        assert response.status_code == status.HTTP_200_OK
        assert company.website in response.text


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
        # delete the entity
        token = await get_company_token(client, company)
        token_header = create_token_header(token)
        response = await client.delete(
            url=f"/companies/{company.id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == None

        # confirm the entity is actually deleted
        response = await client.get(
            url=f"/companies/{company.id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}


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