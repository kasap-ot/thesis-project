import pytest
import psycopg as pg
from .database import get_connection_string


BASE_URL = "http://127.0.0.1:8000"


def create_token_header(token: dict) -> dict:
    return {"Authorization": f"Bearer {token['access_token']}"}


def delete_db_data(db_connection: pg.Connection):
    db_connection.execute("DELETE FROM applications;")
    db_connection.execute("DELETE FROM experiences;")
    db_connection.execute("DELETE FROM offers;")
    db_connection.execute("DELETE FROM students;")
    db_connection.execute("DELETE FROM companies;")
    db_connection.commit()


@pytest.fixture(scope="module")
def db_connection():
    db_string = get_connection_string()
    
    with pg.connect(db_string) as db_connection:
        yield db_connection
        delete_db_data(db_connection)


@pytest.fixture(scope="function", autouse=True)
def reset_database(db_connection: pg.Connection):
    delete_db_data(db_connection)