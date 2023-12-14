from .utils import random_string
from .enums import Status
from pydantic import BaseModel
from datetime import date


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
                    "date": "2018-01-01",
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
    id: int


class StudentUpdate(StudentBase):
    ...
    # email: str | None = None
    # name: str | None = None
    # date_of_birth: int | None = None
    # university: str | None = None
    # major: str | None = None
    # credits: int | None = None
    # gpa: float | None = None


class StudentInDB(StudentBase):
    id: int
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
    id: int


class CompanyUpdate(CompanyBase):
    ...
    # email: str | None = None
    # name: str | None = None
    # field: str | None = None
    # num_employees: int | None = None
    # year_founded: int | None = None
    # website: str | None = None


class CompanyInDB(CompanyBase):
    id: int
    hashed_password: str


""" OFFER SCHEMAS """


class OfferBase(BaseModel):
    salary: int
    num_weeks: int
    field: str
    deadline: date
    requirements: str
    responsibilities: str
    # company_id: int


class OfferCreate(OfferBase):
    company_id: int


class OfferRead(OfferBase):
    id: int
    company_id: int


class OfferUpdate(OfferBase):
    ...
    # salary: int | None = None
    # num_weeks: int | None = None
    # field: str | None = None
    # deadline: date | None = None
    # requirements: str | None = None
    # responsibilities: str | None = None


class OfferBriefRead(BaseModel):
    id: int
    salary: int
    num_weeks: int
    field: str
    deadline: date
    company_name: str


""" EXPERIENCE SCHEMAS """


class ExperienceBase(BaseModel):
    from_date: date
    to_date: date
    company: str
    position: str
    description: str
    # student_id: int


class ExperienceCreate(ExperienceBase):
    student_id: int


class ExperienceRead(ExperienceBase):
    id: int
    student_id: int


class ExperienceUpdate(ExperienceBase):
    ...
    # from_date: date | None = None
    # to_date: date | None = None
    # company: str | None = None
    # position: str | None = None
    # description: str | None = None


""" APPLICATION SCHEMAS """


class ApplicationBase(BaseModel):
    student_id: int
    offer_id: int
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