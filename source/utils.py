import string
import random
from passlib.context import CryptContext


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