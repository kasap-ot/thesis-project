from .enums import UserType
from .database import async_pool
from .utils import pwd_context
from .schemas import StudentInDB, CompanyInDB
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from psycopg.rows import class_row
from dotenv import load_dotenv
from os import getenv


""" Constant variables used for generating JWT tokens """
load_dotenv()
SECRET_KEY = getenv("SECRET_KEY", "")
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
    type: str


def create_token(data: TokenData, expires_delta: timedelta) -> str:
    """
    Helper function. Creates a JWT token with
    defined token data, including expiration time.
    """
    expiration_time = datetime.utcnow() + expires_delta
    data.exp = expiration_time
    data_dict = data.model_dump()
    encoded_jwt = jwt.encode(data_dict, SECRET_KEY, ALGORITHM)
    return encoded_jwt


async def get_user_by_email(email: str, user_type: UserType) -> StudentInDB | CompanyInDB | None:
    if user_type == UserType.STUDENT:
        table_name = "students"
        schema = StudentInDB
    elif user_type == UserType.COMPANY:
        table_name = "companies"
        schema = CompanyInDB

    pool = async_pool()
    
    async with pool.connection() as conn, conn.cursor(row_factory=class_row(schema)) as cur:
        sql = f"SELECT * FROM {table_name} WHERE email = %s"
        await cur.execute(sql, [email])
        user_in_db = await cur.fetchone()
        return user_in_db


async def authenticate_user(email: str, password: str, user_type: UserType) -> StudentInDB | CompanyInDB | None:
    """
    Helper function. Checks if the user exists and
    if the password matches the one in the database.
    If no errors encountered, returns the user, else
    returns None value.
    """
    user_in_db = await get_user_by_email(email, user_type)
    
    if not user_in_db:
        return None
    if not pwd_context.verify(password, user_in_db.hashed_password):
        return None

    return user_in_db


async def get_token(email: str, password: str, user_type: UserType) -> Token:
    """
    Main function. Authenticates the login request.
    Creates a JWT token that will be later used by
    the client for further authorization.
    """
    user_in_db = await authenticate_user(email, password, user_type)
    
    if user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_expiration_delta = timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    token = create_token(
        data=TokenData(sub=email, type=user_type.value),
        expires_delta=token_expiration_delta,
    )

    return Token(access_token=token, token_type="Bearer")


CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticated": "Bearer"},
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> StudentInDB | CompanyInDB:
    """
    Used as a dependency. Requires a valid JWT token
    in the 'Authorization' header. Checks token validity.
    If token is valid, queries the DB and returns the
    user associated with the token. Raises exception
    otherwise.
    """
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        email: str | None = payload.get("sub")
        user_type = payload.get("type")
        if email is None or user_type is None:
            raise CREDENTIALS_EXCEPTION
    except JWTError:
        raise CREDENTIALS_EXCEPTION

    user_type = UserType(user_type)
    user_in_db = await get_user_by_email(email, user_type)

    if user_in_db is None:
        raise CREDENTIALS_EXCEPTION

    return user_in_db


def authorize_user(user_id: int, current_user: StudentInDB | CompanyInDB, Schema) -> None:
    """ 
    Checks if the given user-id matches the provided user 
    and if the user if of correct type. If not, raises a 403 exception. 
    """
    is_invalid_user = current_user.id != user_id
    is_invalid_user_type = type(current_user) is not Schema
    if is_invalid_user_type or is_invalid_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not authorize user",
        )