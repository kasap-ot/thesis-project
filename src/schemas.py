from .utils import random_string
from .enums import Status
from pydantic import BaseModel
from datetime import date
from uuid import UUID


""" STUDENT SCHEMAS """


class StudentBase(BaseModel):
    email: str
    name: str
    date_of_birth: date
    university: str
    major: str
    credits: int
    gpa: float
    # TODO: implement user profile photos


class StudentCreate(StudentBase):
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": random_string(),
                    "name": "Some Name",
                    "date_of_birth": "2018-01-01",
                    "university": "Some University",
                    "major" : "Some Major",
                    "credits": 150,
                    "gpa": 7.50,
                    "password": "secret",
                }
            ]
        }
    }


class StudentRead(StudentBase):
    id: UUID


class StudentUpdate(StudentBase):
    ...


class StudentInDB(StudentBase):
    id: UUID
    hashed_password: str


""" COMPANY SCHEMAS """


class CompanyBase(BaseModel):
    email: str
    name: str
    field: str
    num_employees: int
    year_founded: int
    website: str
    # TODO: implement user profile photos


class CompanyCreate(CompanyBase):
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": random_string(),
                    "name": "Some Name",
                    "field": "Some Field",
                    "num_employees" : 120,
                    "year_founded": 2008,
                    "website": "my.website.org",
                    "password": "secret",
                }
            ]
        }
    }


class CompanyRead(CompanyBase):
    id: UUID


class CompanyUpdate(CompanyBase):
    ...


class CompanyInDB(CompanyBase):
    id: UUID
    hashed_password: str


""" OFFER SCHEMAS """


class OfferBase(BaseModel):
    salary: int
    num_weeks: int
    field: str
    deadline: date
    requirements: str
    responsibilities: str


class OfferCreate(OfferBase):
    company_id: UUID


class OfferRead(OfferBase):
    id: UUID
    company_id: UUID


class OfferUpdate(OfferBase):
    ...


class OfferBriefRead(BaseModel):
    id: UUID
    salary: int
    num_weeks: int
    field: str
    deadline: date
    company_name: str


class OfferApplication(BaseModel):
    field: str
    salary: int
    num_weeks: int
    status: Status
    student_id: UUID
    offer_id: UUID


""" EXPERIENCE SCHEMAS """


class ExperienceBase(BaseModel):
    from_date: date
    to_date: date
    company: str
    position: str
    description: str


class ExperienceCreate(ExperienceBase):
    student_id: UUID


class ExperienceRead(ExperienceBase):
    id: UUID
    student_id: UUID


class ExperienceUpdate(ExperienceBase):
    ...


""" APPLICATION SCHEMAS """


class ApplicationBase(BaseModel):
    student_id: UUID
    offer_id: UUID
    status: Status


class ApplicationRead(ApplicationBase):
    ...


class ApplicationCreate(ApplicationBase):
    ...


""" STUDENT PROFILE SCHEMAS """


class StudentProfileRead(StudentRead):
    experiences: list[ExperienceRead]


class StudentProfileUpdate(StudentUpdate):
    experiences: list[ExperienceUpdate]


class ApplicantRead(StudentRead):
    status: Status