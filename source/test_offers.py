from dataclasses import asdict
from fastapi import status
from httpx import AsyncClient
import pytest
from .test_utils import (
    create_offer,
    create_token_header,
    get_company_header_token,
    insert_offers_in_db,
    insert_company_in_db,
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
        token_header = await get_company_header_token(client, company)
        response = await client.post(
            url="/offers",
            headers=token_header,
            json=asdict(offer),
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == None



@pytest.mark.asyncio
async def test_offer_post_incorrect_field():
    ...


@pytest.mark.asyncio
async def test_offer_post_unauthorized():
    ...


@pytest.mark.asyncio
async def test_offers_get():
    ...


@pytest.mark.asyncio
async def test_offers_get_filtered():
    ...


@pytest.mark.asyncio
async def test_offer_get():
    ...


@pytest.mark.asyncio
async def test_offer_get_not_found():
    ...


@pytest.mark.asyncio
async def test_offer_unauthorized():
    ...


@pytest.mark.asyncio
async def test_offer_edit_get():
    ...


@pytest.mark.asyncio
async def test_offer_edit_get_not_found():
    ...


@pytest.mark.asyncio
async def test_offer_put():
    ...


@pytest.mark.asyncio
async def test_offer_put_incorrect_field():
    ...


@pytest.mark.asyncio
async def test_offer_put_unauthorized():
    ...


@pytest.mark.asyncio
async def test_offer_delete():
    ...


@pytest.mark.asyncio
async def test_offer_delete_not_found():
    ...


@pytest.mark.asyncio
async def test_offer_delete_unauthorized():
    ...