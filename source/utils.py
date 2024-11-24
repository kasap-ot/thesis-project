from passlib.context import CryptContext
from .enums import UserType
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


def extract_user_type(current_user) -> UserType:
    if isinstance(current_user, StudentInDB):
        user_type = UserType.STUDENT
    elif isinstance(current_user, CompanyInDB):
        user_type = UserType.COMPANY
    else:
        raise Exception(f"User must be a student or company. Got: {type(current_user)}")
    return user_type
