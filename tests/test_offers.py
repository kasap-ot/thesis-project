from .fixtures import session_fixture, client_fixture
from ..src.models import OfferCreate, Offer
from fastapi.testclient import TestClient
from fastapi import status
from datetime import date
from sqlmodel import Session
from httpx import Response


FAKE_ID = 500

TEST_CREATE_OFFER = OfferCreate(
    salary=100,
    num_weeks=12,
    field="Particle Physics",
    deadline=date.today(),
    requirements="You have to have some requirements, of course!",
    responsibilities="You will work amazing work and do amazing tasks!",
)


def generate_offer(
    salary=800,
    num_weeks=8,
    field="Some field",
    deadline=date.fromisoformat("2023-01-05"),
    requirements="Some requirements",
    responsibilities="Some responsibilities",
) -> Offer:
    """
    Generates a new Offer object. Required to avoid
    stateful changes when running the tests - cannot
    reuse global variables because some fields might
    be updated while running the tests.
    """
    return Offer(
        salary = salary,
        num_weeks = num_weeks,
        field = field,
        deadline = deadline,
        requirements = requirements,
        responsibilities = responsibilities,
    )


def test_read_nonexistent_offer(client: TestClient):
    response = client.get(f"/offers/{FAKE_ID}")
    data: dict = response.json()

    assert data == {"detail": "Offer not found"}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_offer(client: TestClient, session: Session):
    offer = generate_offer()
    session.add(offer)
    session.commit()

    r = client.get(f"/offers/{offer.id}")
    data: dict = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert data["id"] == offer.id
    assert data["salary"] == offer.salary
    assert data["num_weeks"] == offer.num_weeks
    assert data["field"] == offer.field
    assert data["deadline"] == offer.deadline.isoformat()
    assert data["requirements"] == offer.requirements
    assert data["responsibilities"] == offer.responsibilities


def test_create_invalid_offer(client: TestClient):
    invalid_offer = {
        "salary": 1500,
        "num_weeks": 10,
        "mistake_field": "This should cause an error!",
        "deadline": "2023-01-01",
        "requirements": "Some requirements",
        "responsibilities": "Some responsibilities",
    }

    r = client.post("/offers", json=invalid_offer)

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_offer(client: TestClient):
    response = client.post("/offers", json=TEST_CREATE_OFFER.to_dict())
    data: dict = response.json()

    assert data["salary"] == TEST_CREATE_OFFER.salary
    assert data["num_weeks"] == TEST_CREATE_OFFER.num_weeks
    assert data["field"] == TEST_CREATE_OFFER.field
    assert data["deadline"] == TEST_CREATE_OFFER.deadline.isoformat()
    assert data["requirements"] == TEST_CREATE_OFFER.requirements
    assert data["responsibilities"] == TEST_CREATE_OFFER.responsibilities

    keys = data.keys()
    assert "id" in keys
    assert response.status_code == status.HTTP_201_CREATED



def test_update_offer_invalid(client: TestClient, session: Session):
    offer = generate_offer()
    session.add(offer)
    session.commit()

    new_invalid_value = "This should cause an error!"
    r = client.patch(
        f"/offers/{FAKE_ID}",
        json={"field": new_invalid_value}
    )
    data: dict = r.json()

    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert data == {"detail": "Offer not found"}


def test_update_offer(client: TestClient, session: Session):
    offer = generate_offer()
    session.add(offer)
    session.commit()

    new_value = "Updated field"
    r = client.patch(
        f"/offers/{offer.id}",
        json={"field": new_value}
    )
    data: dict = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert data["id"] == offer.id
    assert data["salary"] == offer.salary
    assert data["num_weeks"] == offer.num_weeks
    assert data["field"] == new_value
    assert data["deadline"] == offer.deadline.isoformat()
    assert data["requirements"] == offer.requirements
    assert data["responsibilities"] == offer.responsibilities


def test_delete_offer_invalid(client: TestClient, session: Session):
    offer = generate_offer()
    session.add(offer)
    session.commit()

    r = client.delete(f"/offers/{FAKE_ID}")
    data: dict = r.json()

    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert data == {"detail": "Offer not found"}


def test_delete_offer(client: TestClient, session: Session):
    offer = generate_offer()
    session.add(offer)
    session.commit()

    r = client.delete(f"/offers/{offer.id}")
    data: dict = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert data["id"] == offer.id
    assert data["salary"] == offer.salary
    assert data["num_weeks"] == offer.num_weeks
    assert data["field"] == offer.field
    assert data["deadline"] == offer.deadline.isoformat()
    assert data["requirements"] == offer.requirements
    assert data["responsibilities"] == offer.responsibilities
