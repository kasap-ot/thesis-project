from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from database import get_session
from utils import pwd_context
from sqlmodel import Session
from models import User, UserRead


""" Constant variables used for generating JWT tokens """
SECRET_KEY = "7705f92e8e0ff13a2d0e30d3f35dd67fc2ad78b1c0c753c674a9edb1f60df4ad"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

"""
Used as a dependency to extract the JWT token 
from the 'Authorization' header. Will supply the 
token as a parameter in the dependable function.
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    """
    A schema for the return type
    when generating the JWT token.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    A schema for what will be stored in the
    JWT token. Can be modified/expanded.
    """
    sub: str | None = None
    exp: datetime | None = None


def create_token(data: TokenData, expires_delta: timedelta) -> str:
    """
    Helper function. Creates a JWT token with
    defined token data, including expiration time.
    """
    expiration_time = datetime.utcnow() + expires_delta
    data.exp = expiration_time
    data_dict = data.dict()
    encoded_jwt = jwt.encode(data_dict, SECRET_KEY, ALGORITHM)
    return encoded_jwt


def authenticate_user(user_id: int, password: str, session: Session) -> User | None:
    """
    Helper function. Checks if the user exists and
    if the password matches the one in the database.
    """
    user_in_db = session.get(User, user_id)

    if not user_in_db:
        return None
    if not pwd_context.verify(password, user_in_db.hashed_password):
        return None

    return user_in_db


def login_for_token(user_id: int, password: str, session: Session) -> Token:
    """
    Main function. Authenticates the login request.
    Creates a JWT token that will be later used by
    the client for further authorization.
    """
    user_in_db = authenticate_user(user_id, password, session)

    if user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_expiration_delta = timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    token = create_token(
        data=TokenData(sub=str(user_in_db.id)),
        expires_delta=token_expiration_delta,
    )

    return Token(access_token=token, token_type="bearer")


""" To reduce code duplication """
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticated": "Bearer"},
)


async def verify_token(token: str = Depends(oauth2_scheme)) -> None:
    """
    Used as a dependency. Requires a valid JWT token in
    the 'Authorization' header. Simply checks validity of
    the token. If token is valid, returns None. Otherwise,
    raises exception.
    """    
    try:
        print("[1]", token)
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        print("[2]")
        user_id: int | None = payload.get("sub")
        if user_id is None:
            print("NO USER ID ERROR!")
            raise credentials_exception
    except JWTError:
        print("JWT ERROR!")
        raise credentials_exception
    
    return None


async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    """
    Used as a dependency. Requires a valid JWT token in
    the 'Authorization' header. Checks token validity. If
    token is valid, queries the DB and returns the user
    associated with the token. Raises exception otherwise.
    """
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        user_id: int | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_in_db = session.get(User, user_id)

    if user_in_db is None:
        raise credentials_exception

    return user_in_db
