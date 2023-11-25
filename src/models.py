from sqlmodel import (SQLModel, Field)


""" Models for USERS """

class StudentBase(SQLModel):
    email: str = Field(unique=True, index=True)
    name: str
    age: int
    university: str
    major: str
    credits: int
    gpa: float


class Student(StudentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    

class StudentCreate(StudentBase):
    password: str


class StudentRead(StudentBase):
    id: int


class StudentUpdate(SQLModel):
    email: str | None = None
    name: str | None = None
    age: int | None = None
    university: str | None = None
    major: str | None = None
    credits: int | None = None
    gpa: float | None = None


""" Models for COMPANIES """

class CompanyBase(SQLModel):
    email: str = Field(unique=True, index=True)
    name: str
    age: int
    field: str
    num_employees: int
    year_founded: int
    website: str


class Company(CompanyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    

class CompanyCreate(CompanyBase):
    password: str


class CompanyRead(CompanyBase):
    id: int


class CompanyUpdate(SQLModel):
    email: str | None = None
    name: str | None = None
    age: int | None = None
    field: str | None = None
    num_employees: int | None = None
    year_founded: int | None = None
    website: str | None = None


"""
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
"""