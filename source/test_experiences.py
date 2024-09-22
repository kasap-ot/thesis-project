from dataclasses import asdict
from fastapi import status
from httpx import AsyncClient
import pytest
from .test_utils import (
    ExperienceTest,
    StudentTest,
    create_experience,
    student_token_header,
    insert_student,
    insert_experience,
    db_connection,
    reset_database,
    OfferTest,
    BASE_URL,
)


@pytest.mark.asyncio
async def test_experience_post(insert_student: StudentTest):
    student = insert_student
    experience = create_experience(student.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = await student_token_header(client, student)
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
async def test_experience_post_incorrect(insert_student: StudentTest):
    student = insert_student
    experience = create_experience(student.id)
    experience.from_date = "This should be a date string..."
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = await student_token_header(client, student)
        response = await client.post(
            url="/experiences",
            headers=headers,
            json=asdict(experience)
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert type(response.json()) == dict


@pytest.mark.asyncio
async def test_experience_post_unauthorized(insert_student: StudentTest):
    student = insert_student
    experience = create_experience(student.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            url="/experiences",
            json=asdict(experience)
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert type(response.json()) == dict


@pytest.mark.asyncio
async def test_experience_patch(insert_experience: dict):
    student: StudentTest = insert_experience["student"]
    experience: ExperienceTest = insert_experience["experience"]
    experience.description = "Test Updated Experience Description"
    async with AsyncClient(base_url=BASE_URL) as client:
        # update the experience
        headers = await student_token_header(client, student)
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
async def test_experience_patch_incorrect(insert_experience: dict):
    student: StudentTest = insert_experience["student"]
    experience: ExperienceTest = insert_experience["experience"]
    experience.from_date = "This should be a date string..."
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = await student_token_header(client, student)
        response = await client.put(
            url=f"/experiences/{experience.id}",
            headers=headers,
            json=asdict(experience)
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert type(response.json()) == dict


@pytest.mark.asyncio
async def test_experience_patch_not_found(insert_student: StudentTest):
    student = insert_student
    fake_experience = create_experience(student.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = await student_token_header(client, student)
        response = await client.put(
            url=f"/experiences/{fake_experience.id}",
            headers=headers,
            json=asdict(fake_experience)
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert type(response.json()) == dict


@pytest.mark.asyncio
async def test_experience_patch_unauthorized(insert_experience: dict):
    experience: ExperienceTest = insert_experience["experience"]
    experience.description = "Test Updated Experience Description"
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.put(
            url=f"/experiences/{experience.id}",
            json=asdict(experience)
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert type(response.json()) == dict


@pytest.mark.asyncio
async def test_experience_delete(insert_experience: dict):
    student: StudentTest = insert_experience["student"]
    experience: ExperienceTest = insert_experience["experience"]
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = await student_token_header(client, student)
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
async def test_experience_delete_not_found(insert_student: StudentTest):
    student = insert_student
    experience = create_experience(student.id)
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = await student_token_header(client, student)
        response = await client.delete(
            url=f"/experiences/{experience.id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert type(response.json()) == dict


@pytest.mark.asyncio
async def test_experience_delete_unauthorized(insert_experience: dict):
    experience: ExperienceTest = insert_experience["experience"]
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.delete(
            url=f"/experiences/{experience.id}",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert type(response.json()) == dict