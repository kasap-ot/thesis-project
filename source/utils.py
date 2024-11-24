import re
from io import BytesIO
from pypdf import PdfReader
import string
import random
from passlib.context import CryptContext
from .enums import Region, UserType
from .schemas import StudentInDB, CompanyInDB


def extract_subjects_from(subjects_string: str) -> list[tuple[str, int]]:
    subjects_list = []
    subjects = subjects_string.split(";")
    for subject in subjects:
        name, grade = subject.split(",")
        grade = int(grade)
        subjects_list.append((name, grade))
    return subjects_list


""" Used to access password hashing utilities. """
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def random_string(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def extract_user_type(current_user) -> UserType:
    if isinstance(current_user, StudentInDB):
        user_type = UserType.STUDENT
    elif isinstance(current_user, CompanyInDB):
        user_type = UserType.COMPANY
    else:
        raise Exception(f"User must be a student or company. Got: {type(current_user)}")
    return user_type
