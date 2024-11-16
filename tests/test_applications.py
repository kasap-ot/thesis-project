from httpx import AsyncClient
from fastapi import status
import pytest
from ..source.enums import Status
from .test_utils import (
    create_offer,
    create_student,
    company_token_header,
    student_token_header,
    applications_from_db,
    insert_student,
    insert_company,
    insert_offers,
    insert_student_applications,
    insert_offer_applications,
    insert_accepted_rejected_applications,
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
async def test_application_post(insert_student: StudentTest, insert_offers: dict):
    student = insert_student
    offers: list[OfferTest] = insert_offers["offers"]
    offer = offers[0]
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await student_token_header(client, student)
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
async def test_application_post_invalid_offer_id(insert_student: StudentTest, insert_company: CompanyTest):
    student = insert_student
    company = insert_company
    offer = create_offer(company.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await student_token_header(client, student)
        response = await client.post(
            url=f"/applications/apply/{student.id}/{offer.id}",
            headers=token_header,
        )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert type(response.json()) == dict
    assert "detail" in response.text


# test appliction post no student credentials
@pytest.mark.asyncio
async def test_application_post_unauthorized(insert_offers: dict):
    student = create_student()
    offers: list[OfferTest] = insert_offers["offers"]
    offer = offers[0]
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(url=f"/applications/apply/{student.id}/{offer.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.text


@pytest.mark.asyncio
async def test_applications_get(insert_student_applications):
    student = insert_student_applications["student"]
    offers: list[OfferTest] = insert_student_applications["offers"]
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await student_token_header(client, student)
        response = await client.get(
            url=f"/applications/view/{student.id}",
            headers=token_header,
        )
    assert response.status_code == status.HTTP_200_OK
    for offer in offers:
        assert offer.field in response.text
        assert str(offer.salary) in response.text
        assert str(offer.num_weeks) in response.text


@pytest.mark.asyncio
async def test_applications_get_no_application(insert_student):
    student = insert_student
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await student_token_header(client, student)
        response = await client.get(
            url=f"/applications/view/{student.id}",
            headers=token_header,
        )
    assert response.status_code == status.HTTP_200_OK
    assert "<div>" in response.text
    assert "</div>" in response.text


@pytest.mark.asyncio
async def test_applications_get_unauthorized(insert_student_applications):
    student = insert_student_applications["student"]
    
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get(
            url=f"/applications/view/{student.id}",
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.text


@pytest.mark.asyncio
async def test_application_accept(insert_offer_applications):
    db_data = insert_offer_applications
    students: list[StudentTest] = db_data["students"]
    first_student = students[0]
    offer: OfferTest = db_data["offer"]
    company: CompanyTest = db_data["company"]
    
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await company_token_header(client, company)
        response = await client.patch(
            url=f"/applications/accept/{first_student.id}/{offer.id}",
            headers=token_header
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == None

    # check if application statuses were updated correctly
    
    updated_applications = applications_from_db(offer.id)
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


@pytest.mark.asyncio
async def test_application_cancel(insert_offer_applications):
    db_data = insert_offer_applications
    students: list[StudentTest] = db_data["students"]
    inserted_applications: list[ApplicationTest] = db_data["applications"]
    cancelling_student = students[0]
    offer: OfferTest = db_data["offer"]
    
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await student_token_header(client, cancelling_student)
        response = await client.delete(
            url=f"/applications/cancel/{cancelling_student.id}/{offer.id}",
            headers=token_header,
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == None

    # check that the application is deleted and others remain

    updated_applications = applications_from_db(offer.id)

    assert all(
        application.status == Status.WAITING.value 
        for application in updated_applications
    )
    assert len(updated_applications) == len(inserted_applications) - 1


@pytest.mark.asyncio
async def test_application_cancel_accepted(insert_accepted_rejected_applications):
    db_data = insert_accepted_rejected_applications
    students: list[StudentTest] = db_data["students"]
    inserted_applications: list[ApplicationTest] = db_data["applications"]
    cancelling_student = students[0]
    offer: OfferTest = db_data["offer"]

    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await student_token_header(client, cancelling_student)
        response = await client.delete(
            url=f"/applications/cancel/{cancelling_student.id}/{offer.id}",
            headers=token_header,
        )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == None

    # check that the application is removed
    updated_applications = applications_from_db(offer.id)
    assert len(updated_applications) == len(inserted_applications) - 1
    assert cancelling_student.id not in [application.student_id for application in updated_applications]

    # check that the other applications are reset
    assert all(
        application.status == Status.WAITING.value 
        for application in updated_applications
    )
    

@pytest.mark.asyncio
async def test_applicants_get(insert_offer_applications):
    db_data = insert_offer_applications
    company: CompanyTest = db_data["company"]
    offer: OfferTest = db_data["offer"]
    students: list[StudentTest] = db_data["students"]
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await company_token_header(client, company)
        response = await client.get(
            url=f"/applications/applicants/{offer.id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text
        for student in students:
            assert student.name in response.text


@pytest.mark.asyncio
async def test_applicants_get_empty(insert_offers):
    db_data = insert_offers
    company: CompanyTest = db_data["company"]
    offer: OfferTest = db_data["offers"][0]
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await company_token_header(client, company)
        response = await client.get(
            url=f"/applications/applicants/{offer.id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert "<div>" in response.text


@pytest.mark.asyncio
async def test_applicants_get_no_offers(insert_company: CompanyTest):
    company = insert_company
    fake_offer = create_offer(company.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        token_header = await company_token_header(client, company)
        response = await client.get(
            url=f"/applications/applicants/{fake_offer.id}",
            headers=token_header,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND