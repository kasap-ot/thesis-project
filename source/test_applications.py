from httpx import AsyncClient
from fastapi import status
from dataclasses import asdict
import pytest
from .enums import Status
from .test_utils import (
    create_application,
    create_offer,
    create_student,
    get_company_token_header,
    get_student_token_header,
    get_applications_from_db,
    insert_student_in_db,
    insert_company_in_db,
    insert_offers_in_db,
    insert_student_applications_in_db,
    insert_offer_applications_in_db,
    db_connection,
    reset_database,
    ApplicationTest,
    StudentTest,
    OfferTest,
    CompanyTest,
    BASE_URL,
)


# test_application_post
@pytest.mark.asyncio
async def test_application_post(insert_student_in_db: StudentTest, insert_offers_in_db: dict):
    student = insert_student_in_db
    offers: list[OfferTest] = insert_offers_in_db["offers"]
    offer = offers[0]
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await get_student_token_header(client, student)
        response = await client.post(
            url=f"/applications/apply/{student.id}/{offer.id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == None

        # check if inserted correctly
        response = await client.get(
           url=f"/applications/view/{student.id}",
           headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert offer.field in response.text
        assert str(offer.salary) in response.text


# test application post incorrect
@pytest.mark.asyncio
async def test_application_post_invalid_offer_id(insert_student_in_db: StudentTest, insert_company_in_db: CompanyTest):
    student = insert_student_in_db
    company = insert_company_in_db
    offer = create_offer(company.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await get_student_token_header(client, student)
        response = await client.post(
            url=f"/applications/apply/{student.id}/{offer.id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert type(response.json()) == dict
        assert "detail" in response.text


# test appliction post no student credentials
@pytest.mark.asyncio
async def test_application_post_unauthorized(insert_offers_in_db: dict):
    student = create_student()
    offers: list[OfferTest] = insert_offers_in_db["offers"]
    offer = offers[0]
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(url=f"/applications/apply/{student.id}/{offer.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.text


# test_applications_get
@pytest.mark.asyncio
async def test_applications_get(insert_student_applications_in_db):
    student = insert_student_applications_in_db["student"]
    offers: list[OfferTest] = insert_student_applications_in_db["offers"]
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await get_student_token_header(client, student)
        response = await client.get(
            url=f"/applications/view/{student.id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        for offer in offers:
            assert offer.field in response.text
            assert str(offer.salary) in response.text
            assert str(offer.num_weeks) in response.text


# test applications get no application
@pytest.mark.asyncio
async def test_applications_get_no_application(insert_student_in_db, insert_company_in_db):
    student = insert_student_in_db
    company = insert_company_in_db
    offer = create_offer(company.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await get_student_token_header(client, student)
        response = await client.get(
            url=f"/applications/view/{student.id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        assert "</div>" in response.text


# test application get not authorized
@pytest.mark.asyncio
async def test_applications_get_unauthorized(insert_student_applications_in_db):
    student = insert_student_applications_in_db["student"]
    offers: list[OfferTest] = insert_student_applications_in_db["offers"]
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get(
            url=f"/applications/view/{student.id}",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.text


# test_application_accept
@pytest.mark.asyncio
async def test_application_accept(insert_offer_applications_in_db):
    db_data = insert_offer_applications_in_db
    students: list[StudentTest] = db_data["students"]
    first_student = students[0]
    offer: OfferTest = db_data["offer"]
    company: CompanyTest = db_data["company"]
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await get_company_token_header(client, company)
        response = await client.patch(
            url=f"/applications/accept/{first_student.id}/{offer.id}",
            headers=token_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == None

        # check if application statuses were updated correctly
        
        updated_applications = get_applications_from_db(offer.id)
        accepted_applications = [
            application for application in updated_applications 
            if application.status == Status.ACCEPTED.value
        ]
        rejected_applications  = [
            application for application in updated_applications 
            if application.status == Status.REJECTED.value
        ]
        
        # check that only one student is selected
        
        assert len(accepted_applications) == 1
        accepted_application = accepted_applications[0]
        assert accepted_application == ApplicationTest(first_student.id, offer.id, Status.ACCEPTED.value)
        
        # check that all others are rejected
        assert len(rejected_applications) == len(updated_applications) - len(accepted_applications)




# test_application_cancel


# test_applicants_get