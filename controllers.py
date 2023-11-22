from models import UserCreate, User, UserUpdate
from sqlmodel import Session, select
from fastapi import HTTPException, status
from utils import pwd_context


def register_user(user: UserCreate, session: Session) -> User:
    sql = select(User).where(User.email == user.email)
    user_in_db = session.exec(sql).first()
    if user_in_db is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    hashed_password = pwd_context.hash(user.password)
    user_to_insert = User(
        **user.dict(),
        hashed_password=hashed_password,
    )
    session.add(user_to_insert)
    session.commit()
    session.refresh(user_to_insert)

    return user_to_insert


def get_users(session: Session) -> list[User]:
    sql = select(User)
    users = session.exec(sql).all()
    return list(users)


def get_user(user_id: int, session: Session) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def get_user_by_email(email: str, session: Session) -> User:
    sql = select(User).where(User.email == email)
    user = session.exec(sql).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def update_user(
    user_id: int, update_user: UserUpdate, session: Session, current_user: User
) -> User:
    if current_user.id != user_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Action is not allowed",
        )
    user = get_user(user_id, session)
    updated_fields = update_user.dict(exclude_unset=True)
    for key, value in updated_fields.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(user_id: int, session: Session, current_user: User) -> User:
    if current_user.id != user_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Action is not allowed",
        )
    user = get_user(user_id, session)
    session.delete(user)
    session.commit()
    return user
