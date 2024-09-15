from dataclasses import asdict
from fastapi import status
from httpx import AsyncClient
import pytest
from .test_utils import (
    StudentTest,
    create_offer,
    create_token_header,
    get_company_token_header,
    get_student_token_header,
    insert_offers_in_db,
    insert_company_in_db,
    insert_student_in_db,
    get_company_token,
    db_connection,
    reset_database,
    CompanyTest,
    OfferTest,
    BASE_URL,
)


@pytest.mark.asyncio
async def test_offer_create_get():
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/offers-create")
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert "</div>" in response.text


@pytest.mark.asyncio
async def test_offer_post(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    offer = create_offer(company_id=company.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await get_company_token_header(client, company)
        response = await client.post(
            url="/offers",
            headers=token_header,
            json=asdict(offer),
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == None



@pytest.mark.asyncio
async def test_offer_post_incorrect_field(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    offer = create_offer(company_id=company.id)
    offer.num_weeks = "This should be an integer" # type: ignore
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await get_company_token_header(client, company)
        response = await client.post(
            url="/offers",
            headers=token_header,
            json=asdict(offer),
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.text


@pytest.mark.asyncio
async def test_offer_post_unauthorized(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    offer = create_offer(company_id=company.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            url="/offers",
            json=asdict(offer),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.text


@pytest.mark.asyncio
async def test_offers_get(insert_offers_in_db: dict, insert_student_in_db: StudentTest):
    offers: list[OfferTest] = insert_offers_in_db["offers"]
    student = insert_student_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await get_student_token_header(client, student)
        response = await client.get(
            url="/offers",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert offers[0].field in response.text
        assert offers[1].field in response.text
        assert offers[2].field in response.text



@pytest.mark.asyncio
async def test_offers_get_filtered(insert_offers_in_db: dict, insert_student_in_db: StudentTest):
    offers: list[OfferTest] = insert_offers_in_db["offers"]
    student = insert_student_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await get_student_token_header(client, student)
        url = "/offers?"
        url += f"field={offers[0].field}"
        url += f"&max_num_weeks={offers[0].num_weeks}"
        response = await client.get(
            url=url,
            headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert offers[0].field in response.text
        assert offers[1].field not in response.text
        assert offers[2].field not in response.text


@pytest.mark.asyncio
async def test_offer_get(insert_offers_in_db: dict, insert_student_in_db: StudentTest):
    offers: list[OfferTest] = insert_offers_in_db["offers"]
    student = insert_student_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await get_student_token_header(client, student)
        response = await client.get(
            url=f"/offers/{offers[0].id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert offers[0].field in response.text
        assert offers[1].field not in response.text
        assert offers[2].field not in response.text


@pytest.mark.asyncio
async def test_offer_get_not_found(insert_student_in_db: StudentTest, insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    fake_offer = create_offer(company.id)
    student = insert_student_in_db
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await get_student_token_header(client, student)
        response = await client.get(
            url=f"/offers/{fake_offer.id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_offer_get_unauthorized(insert_offers_in_db: dict):
    offers: list[OfferTest] = insert_offers_in_db["offers"]
    async with AsyncClient(base_url=BASE_URL) as client:
        url = f"/offers/{offers[0].id}"
        response = await client.get(url=url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_offer_edit_get(insert_offers_in_db: dict):
    offers: list[OfferTest] = insert_offers_in_db["offers"]
    async with AsyncClient(base_url=BASE_URL) as client:
        url = f"/offers/{offers[0].id}/edit"
        response = await client.get(url=url)
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert offers[0].responsibilities in response.text


@pytest.mark.asyncio
async def test_offer_edit_get_not_found(insert_company_in_db: CompanyTest):
    company = insert_company_in_db
    fake_offer = create_offer(company.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        url = f"/offers/{fake_offer.id}/edit"
        response = await client.get(url=url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()



@pytest.mark.asyncio
async def test_offer_put(insert_offers_in_db: dict):
    company: CompanyTest = insert_offers_in_db["company"]
    offers: list[OfferTest] = insert_offers_in_db["offers"]
    first_offer = offers[0]
    first_offer.field = "This field is updated!"
    async with AsyncClient(base_url=BASE_URL) as client:
        # update the entity
        token_header = await get_company_token_header(client, company)
        response = await client.put(
            url=f"/offers/{first_offer.id}",
            headers=token_header,
            json=asdict(first_offer),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == None
        
        # check if the entitty is updated
        response = await client.get(
            url=f"/offers/{offers[0].id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert first_offer.field in response.text


@pytest.mark.asyncio
async def test_offer_put_incorrect_field(insert_offers_in_db: dict):
    company: CompanyTest = insert_offers_in_db["company"]
    offers: list[OfferTest] = insert_offers_in_db["offers"]
    first_offer = offers[0]
    first_offer.num_weeks = "This should be an integer!" # type: ignore
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await get_company_token_header(client, company)
        response = await client.put(
            url=f"/offers/{first_offer.id}",
            headers=token_header,
            json=asdict(first_offer),
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        print(response.json())
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_offer_put_unauthorized(insert_offers_in_db: dict):
    company: CompanyTest = insert_offers_in_db["company"]
    offers: list[OfferTest] = insert_offers_in_db["offers"]
    first_offer = offers[0]
    first_offer.field = "This field is updated!"
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.put(
            url=f"/offers/{first_offer.id}",
            json=asdict(first_offer),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        print(response.json())
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_offer_delete():
    ...


@pytest.mark.asyncio
async def test_offer_delete_not_found():
    ...


@pytest.mark.asyncio
async def test_offer_delete_unauthorized():
    ...