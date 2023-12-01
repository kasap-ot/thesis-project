from .enums import Status
from pydantic import BaseModel, Field
from datetime import date


""" STUDENT SCHEMAS """


class StudentBase(BaseModel):
    email: str
    name: str
    age: int
    university: str
    major: str
    credits: int
    gpa: float


class StudentCreate(StudentBase):
    password: str


class StudentRead(StudentBase):
    id: int


class StudentUpdate(BaseModel):
    email: str | None = None
    name: str | None = None
    age: int | None = None
    university: str | None = None
    major: str | None = None
    credits: int | None = None
    gpa: float | None = None


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


class CompanyCreate(CompanyBase):
    password: str


class CompanyRead(CompanyBase):
    id: int


class CompanyUpdate(BaseModel):
    email: str | None = None
    name: str | None = None
    field: str | None = None
    num_employees: int | None = None
    year_founded: int | None = None
    website: str | None = None


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
    company_id: int


class OfferCreate(OfferBase):
    ...


class OfferRead(OfferBase):
    id: int


class OfferUpdate(BaseModel):
    salary: int | None = None
    num_weeks: int | None = None
    field: str | None = None
    deadline: date | None = None
    requirements: str | None = None
    responsibilities: str | None = None


""" EXPERIENCE SCHEMAS """


class ExperienceBase(BaseModel):
    from_date: date
    to_date: date
    company: str
    position: str
    description: str
    student_id: int


class ExperienceCreate(ExperienceBase):
    ...


class ExperienceRead(ExperienceBase):
    id: int


class ExperienceUpdate(BaseModel):
    from_date: date | None = None
    to_date: date | None = None
    company: str | None = None
    position: str | None = None
    description: str | None = None


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


class StudentProfile(StudentRead):
    experiences: list[ExperienceRead]
