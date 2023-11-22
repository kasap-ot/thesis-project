from sqlmodel import create_engine, SQLModel, Session


# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"
sqlite_url = f"sqlite://"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


"""
from schemas import UserInDB

fake_db: dict = {}

def get_user(db: dict, username: str) -> UserInDB | None:
    """"""
    Helper function. Retrieves the user
    with the defined username from the DB.
    """"""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None
"""