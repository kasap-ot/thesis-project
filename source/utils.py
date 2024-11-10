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


def extract_file_offer(offer_file_bytes: bytes) -> dict:
    offer_bytes_obj = BytesIO(offer_file_bytes)
    file_reader = PdfReader(offer_bytes_obj)

    text = ""
    for page in file_reader.pages:
        text += page.extract_text()

    offer_info = extract_text_offer_info(text)
    
    return offer_info


def extract_text_offer_info(text: str) -> dict:
    # search for the values
    salary_match = re.search(r"Salary:\s*(\d+)", text)
    weeks_match = re.search(r"Weeks:\s*(\d+)", text)
    field_match = re.search(r"Field:\s*([A-Za-z\s]+)\n", text)
    deadline_match = re.search(r"Deadline:\s*(\d{4}-\d{2}-\d{2})", text)
    region_match = re.search(r"Region:\s*([A-Za-z]+)", text)
    requirements_match = re.search(r"Requirements:\s+([\s\S]+?)\nResponsibilities", text)
    responsibilities_match = re.search(r"Responsibilities:\s+([\s\S]+)$", text)
    
    # check for missing values
    if not salary_match:
        raise Exception("Could not extract salary from file")
    if not weeks_match:
        raise Exception("Could not extract weeks from file text.")
    if not field_match:
        raise Exception("Could not extract field from file text.")
    if not deadline_match:
        raise Exception("Could not extract deadline from file text.")
    if not region_match:
        raise Exception("Could not extract region from file text.")
    if not requirements_match:
        raise Exception("Could not extract requirements from file text.")
    if not responsibilities_match:
        raise Exception("Could not extract responsibilities from file text.")
    
    # extract values
    salary = salary_match.group(1)
    num_weeks = weeks_match.group(1)
    field = field_match.group(1)
    deadline = deadline_match.group(1)
    region = region_match.group(1)
    requirements = requirements_match.group(1)
    responsibilities = responsibilities_match.group(1)

    # post-process values
    salary = int(salary)
    num_weeks = int(num_weeks)
    region_id = convert_to_region_id(region)

    return {
        "salary": salary,
        "num_weeks": num_weeks,
        "field": field,
        "deadline": deadline,
        "requirements": requirements,
        "responsibilities": responsibilities,
        "region_id": region_id,
    }


def convert_to_region_id(region: str) -> int:
    if region == "Global":
        return Region.GLOBAL.value
    elif region == "Europe":
        return Region.EUROPE.value
    elif region == "Asia":
        return Region.ASIA.value
    elif region == "Americas":
        return Region.AMERICAS.value
    else:
        raise Exception(f"Invalid region provided: {region}")


def extract_user_type(current_user) -> UserType:
    if isinstance(current_user, StudentInDB):
        user_type = UserType.STUDENT
    elif isinstance(current_user, CompanyInDB):
        user_type = UserType.COMPANY
    else:
        raise Exception(f"User must be a student or company. Got: {type(current_user)}")
    return user_type
