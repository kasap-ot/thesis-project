from dataclasses import asdict
from fastapi import status
from httpx import AsyncClient
import pytest
from .test_utils import (
    ExperienceTest,
    StudentTest,
    create_experience,
    get_student_token_header,
    insert_student_in_db,
    insert_experience_in_db,
    db_connection,
    reset_database,
    OfferTest,
    BASE_URL,
)


@pytest.mark.asyncio
async def test_experience_post(insert_student_in_db: StudentTest):
    student = insert_student_in_db
    experience = create_experience(student.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = await get_student_token_header(client, student)
        response = await client.post(
            url="/experiences",
            headers=headers,
            json=asdict(experience)
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == None

        # check if is actually inserted
        response = await client.get(
            url=f"/students/profile/{student.id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert experience.description in response.text



@pytest.mark.asyncio
async def test_experience_post_incorrect(insert_student_in_db: StudentTest):
    student = insert_student_in_db
    experience = create_experience(student.id)
    experience.from_date = "This should be a date string..."
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = await get_student_token_header(client, student)
        response = await client.post(
            url="/experiences",
            headers=headers,
            json=asdict(experience)
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert type(response.json()) == dict


@pytest.mark.asyncio
async def test_experience_post_unauthorized(insert_student_in_db: StudentTest):
    student = insert_student_in_db
    experience = create_experience(student.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            url="/experiences",
            json=asdict(experience)
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert type(response.json()) == dict


@pytest.mark.asyncio
async def test_experience_patch(insert_experience_in_db: dict):
    student: StudentTest = insert_experience_in_db["student"]
    experience: ExperienceTest = insert_experience_in_db["experience"]
    experience.description = "Test Updated Experience Description"
    async with AsyncClient(base_url=BASE_URL) as client:
        # update the experience
        headers = await get_student_token_header(client, student)
        response = await client.put(
            url=f"/experiences/{experience.id}",
            headers=headers,
            json=asdict(experience)
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == None

        # check if update was successful
        response = await client.get(
            url=f"/students/profile/{student.id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert experience.description in response.text


@pytest.mark.asyncio
async def test_experience_patch_incorrect(insert_experience_in_db: dict):
    student: StudentTest = insert_experience_in_db["student"]
    experience: ExperienceTest = insert_experience_in_db["experience"]
    experience.from_date = "This should be a date string..."
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = await get_student_token_header(client, student)
        response = await client.put(
            url=f"/experiences/{experience.id}",
            headers=headers,
            json=asdict(experience)
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert type(response.json()) == dict


@pytest.mark.asyncio
async def test_experience_patch_not_found(insert_student_in_db: StudentTest):
    student = insert_student_in_db
    fake_experience = create_experience(student.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = await get_student_token_header(client, student)
        response = await client.put(
            url=f"/experiences/{fake_experience.id}",
            headers=headers,
            json=asdict(fake_experience)
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert type(response.json()) == dict


@pytest.mark.asyncio
async def test_experience_patch_unauthorized(insert_experience_in_db: dict):
    experience: ExperienceTest = insert_experience_in_db["experience"]
    experience.description = "Test Updated Experience Description"
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.put(
            url=f"/experiences/{experience.id}",
            json=asdict(experience)
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert type(response.json()) == dict


@pytest.mark.asyncio
async def test_experience_delete(insert_experience_in_db: dict):
    student: StudentTest = insert_experience_in_db["student"]
    experience: ExperienceTest = insert_experience_in_db["experience"]
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = await get_student_token_header(client, student)
        response = await client.delete(
            url=f"/experiences/{experience.id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == None

        # confirm was deleted successfully
        response = await client.get(
            url=f"/students/profile/{student.id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert experience.description not in response.text


@pytest.mark.asyncio
async def test_experience_delete_not_found(insert_student_in_db: StudentTest):
    student = insert_student_in_db
    experience = create_experience(student.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = await get_student_token_header(client, student)
        response = await client.delete(
            url=f"/experiences/{experience.id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert type(response.json()) == dict


@pytest.mark.asyncio
async def test_experience_delete_unauthorized(insert_experience_in_db: dict):
    experience: ExperienceTest = insert_experience_in_db["experience"]
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.delete(
            url=f"/experiences/{experience.id}",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert type(response.json()) == dict