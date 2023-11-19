from pydantic import BaseModel
from datetime import date
from enums import Status


class Base(BaseModel):
    id: int


class Country(Base):
    name: str


class User(Base):
    email: str
    password: str
    name: str
    country_id: int


class Company(User):
    field: str
    num_employees: int
    year_founded: int
    website: str


class Student(User):
    university: str
    major: str
    credits: int


class Experience(Base):
    from_date: date
    to_date: date
    company: str
    description: str


class Offer(Base):
    country_id: int
    salary: int
    num_weeks: int
    field: str
    deadline: date
    company_id: int
    requirements: str
    responsibilities: str
    # min_year: int (not necessary?)


class Application(Base):
    student_id: int
    offer_id: int
    status: Status
