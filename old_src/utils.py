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
