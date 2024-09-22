from dataclasses import asdict
from fastapi import status
from httpx import AsyncClient
import pytest
from .test_utils import (
    StudentTest,
    create_offer,
    create_token_header,
    company_token_header,
    student_token_header,
    insert_offers,
    insert_company,
    insert_student,
    company_token,
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
async def test_offer_post(insert_company: CompanyTest):
    company = insert_company
    offer = create_offer(company_id=company.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await company_token_header(client, company)
        response = await client.post(
            url="/offers",
            headers=token_header,
            json=asdict(offer),
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == None



@pytest.mark.asyncio
async def test_offer_post_incorrect_field(insert_company: CompanyTest):
    company = insert_company
    offer = create_offer(company_id=company.id)
    offer.num_weeks = "This should be an integer" # type: ignore
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await company_token_header(client, company)
        response = await client.post(
            url="/offers",
            headers=token_header,
            json=asdict(offer),
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.text


@pytest.mark.asyncio
async def test_offer_post_unauthorized(insert_company: CompanyTest):
    company = insert_company
    offer = create_offer(company_id=company.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            url="/offers",
            json=asdict(offer),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.text


@pytest.mark.asyncio
async def test_offers_get(insert_offers: dict, insert_student: StudentTest):
    offers: list[OfferTest] = insert_offers["offers"]
    student = insert_student
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await student_token_header(client, student)
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
async def test_offers_get_filtered(insert_offers: dict, insert_student: StudentTest):
    offers: list[OfferTest] = insert_offers["offers"]
    student = insert_student
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await student_token_header(client, student)
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
async def test_offer_get(insert_offers: dict, insert_student: StudentTest):
    offers: list[OfferTest] = insert_offers["offers"]
    student = insert_student
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await student_token_header(client, student)
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
async def test_offer_get_not_found(insert_student: StudentTest, insert_company: CompanyTest):
    company = insert_company
    fake_offer = create_offer(company.id)
    student = insert_student
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await student_token_header(client, student)
        response = await client.get(
            url=f"/offers/{fake_offer.id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_offer_get_unauthorized(insert_offers: dict):
    offers: list[OfferTest] = insert_offers["offers"]
    async with AsyncClient(base_url=BASE_URL) as client:
        url = f"/offers/{offers[0].id}"
        response = await client.get(url=url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_offer_edit_get(insert_offers: dict):
    offers: list[OfferTest] = insert_offers["offers"]
    async with AsyncClient(base_url=BASE_URL) as client:
        url = f"/offers/{offers[0].id}/edit"
        response = await client.get(url=url)
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert offers[0].responsibilities in response.text


@pytest.mark.asyncio
async def test_offer_edit_get_not_found(insert_company: CompanyTest):
    company = insert_company
    fake_offer = create_offer(company.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        url = f"/offers/{fake_offer.id}/edit"
        response = await client.get(url=url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()



@pytest.mark.asyncio
async def test_offer_put(insert_offers: dict):
    company: CompanyTest = insert_offers["company"]
    offers: list[OfferTest] = insert_offers["offers"]
    first_offer = offers[0]
    first_offer.field = "This field is updated!"
    async with AsyncClient(base_url=BASE_URL) as client:
        # update the entity
        token_header = await company_token_header(client, company)
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
async def test_offer_put_incorrect_field(insert_offers: dict):
    company: CompanyTest = insert_offers["company"]
    offers: list[OfferTest] = insert_offers["offers"]
    first_offer = offers[0]
    first_offer.num_weeks = "This should be an integer!" # type: ignore
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await company_token_header(client, company)
        response = await client.put(
            url=f"/offers/{first_offer.id}",
            headers=token_header,
            json=asdict(first_offer),
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_offer_put_unauthorized(insert_offers: dict):
    offers: list[OfferTest] = insert_offers["offers"]
    first_offer = offers[0]
    first_offer.field = "This field is updated!"
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.put(
            url=f"/offers/{first_offer.id}",
            json=asdict(first_offer),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_offer_delete(insert_offers: dict):
    company = insert_offers["company"]
    offers: list[OfferTest] = insert_offers["offers"]
    first_offer = offers[0]
    async with AsyncClient(base_url=BASE_URL) as client:
        # delete the entity
        token_header = await company_token_header(client, company)
        response = await client.delete(
            url=f"/offers/{first_offer.id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == None

        # check if deleted successfully
        response = await client.get(
            url=f"/companies/{company.id}/offers",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert first_offer.field not in response.text


@pytest.mark.asyncio
async def test_offer_delete_not_found(insert_company: CompanyTest):
    company = insert_company
    fake_offer = create_offer(company.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await company_token_header(client, company)
        response = await client.delete(
            url=f"/offers/{fake_offer.id}",
            headers=token_header
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_offer_delete_unauthorized(insert_offers: dict):
    company = insert_offers["company"]
    offers: list[OfferTest] = insert_offers["offers"]
    first_offer = offers[0]
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.delete(url=f"/offers/{first_offer.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()