from schemas import UserInDB


fake_db: dict = {}


def get_user(db: dict, username: str) -> UserInDB | None:
    """
    Helper function. Retrieves the user
    with the defined username from the DB.
    """
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None
