import os
import time
import shutil
from fastapi import UploadFile, HTTPException, status
from psycopg import AsyncConnection
from psycopg.rows import dict_row
from .schemas import StudentInDB, CompanyInDB
from .utils import extract_user_type
from .queries import (
    select_user_profile_picture_query,
    update_profile_picture_path_query, 
)


PROFILE_IMAGES_FOLDER = "static/img"


def generate_profile_picture_file_name(current_user) -> str:
    if isinstance(current_user, StudentInDB):
        file_name = f"student_{current_user.id}"
    elif isinstance(current_user, CompanyInDB):
        file_name = f"company_{current_user.id}"
    else:
        raise TypeError(f"User must be of type student or company. Got: {type(current_user)}")
    
    timestamp = time.time()
    timestamp = str(timestamp).replace(".", "")

    file_name = f"{file_name}_{timestamp}.jpg"
    return file_name
    

def generate_profile_picture_file_path(current_user) -> str:
    file_name = generate_profile_picture_file_name(current_user)
    return f"{PROFILE_IMAGES_FOLDER}/{file_name}"


async def save_profile_picture(picture: UploadFile, current_user) -> str:
    file_path = generate_profile_picture_file_path(current_user)

    try:
        with open(file_path, "wb") as writer:
            shutil.copyfileobj(picture.file, writer)
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {exception}",
        )
    finally:
        await picture.close()

    return file_path


def delete_profile_picture(file_path: str):
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"File does not exists: {file_path}",
        )
    
    try:
        os.remove(file_path)

    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete file: {exception}",
        )
    

async def save_profile_picture_path(current_user, file_path: str, connection: AsyncConnection) -> None:
    user_type = extract_user_type(current_user)
    query = update_profile_picture_path_query(user_type)
    await connection.execute(query, [file_path, current_user.id])


async def old_profile_picture_path(current_user, connection: AsyncConnection) -> str:
    cursor = connection.cursor(row_factory=dict_row)
    user_type = extract_user_type(current_user)
    query = select_user_profile_picture_query(user_type)
    await cursor.execute(query, [current_user.id])
    record = await cursor.fetchone()

    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    
    return record["profile_picture_path"]