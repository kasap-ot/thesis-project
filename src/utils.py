import string
import random
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from .models import Student, Company


""" Temporary helper function """
def random_color():
    colors = [
        "primary",
        "secondary",
        "success",
        "danger",
        "warning",
        "info",
        "light",
        "dark",
    ]
    return random.choice(colors)

""" Setting temporary env variables for the templates """
templates = Jinja2Templates(directory="templates")
templates.env.filters["random_color"] = random_color


""" Used to access password hashing utilities. """
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def random_string(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def generate_student() -> Student:
    return Student(
        email=random_string(),
        name=random_string(),
        age=random.randint(10, 80),
        hashed_password=random_string(),
        university=random_string(),
        major=random_string(),
        credits=random.randint(0, 180),
        gpa=random.random() * 10,
    )


def generate_company() -> Company:
    return Company(
        email=random_string(),
        name=random_string(),
        age=random.randint(10, 80),
        hashed_password=random_string(),
        field=random_string(),
        num_employees=random.randint(5, 500),
        year_founded=random.randint(1980, 2023),
        website=random_string(),
    )