from typing import Optional
from .enums import Status
from pydantic import BaseModel
from datetime import date


# MOTIVATIONAL LETTER SCHEMAS


class MotivationalLetter(BaseModel):
    student_id: int
    about_me_section: str
    skills_section: str
    looking_for_section: str


class MotivationalLetterRead(BaseModel):
    student_id: Optional[int]
    about_me_section: Optional[str]
    skills_section: Optional[str]
    looking_for_section: Optional[str]


# STUDENT SCHEMAS


class StudentBase(BaseModel):
    email: str
    name: str
    date_of_birth: date
    university: str
    major: str
    credits: int
    gpa: float
    region_id: int


class StudentCreate(StudentBase):
    password: str


class StudentRead(StudentBase):
    id: int
    motivational_letter: MotivationalLetterRead


class StudentUpdate(StudentBase):
    ...


class StudentInDB(StudentBase):
    id: int
    hashed_password: str


# COMPANY SCHEMAS


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


class CompanyUpdate(CompanyBase):
    ...


class CompanyInDB(CompanyBase):
    id: int
    hashed_password: str


# OFFER SCHEMAS


class OfferBase(BaseModel):
    salary: int
    num_weeks: int
    field: str
    deadline: date
    requirements: str
    responsibilities: str


class OfferCreate(OfferBase):
    company_id: int
    region_id: int


class OfferRead(OfferBase):
    id: int
    company_id: int
    region: str


class OfferUpdate(OfferBase):
    ...


class OfferBriefRead(BaseModel):
    id: int
    salary: int
    num_weeks: int
    field: str
    deadline: date
    company_name: str
    region: str


class OfferApplication(BaseModel):
    field: str
    salary: int
    num_weeks: int
    status: Status
    student_id: int
    offer_id: int


# EXPERIENCE SCHEMAS


class ExperienceBase(BaseModel):
    from_date: date
    to_date: date
    company: str
    position: str
    description: str


class ExperienceCreate(ExperienceBase):
    student_id: int


class ExperienceRead(ExperienceBase):
    id: int
    student_id: int


class ExperienceUpdate(ExperienceBase):
    ...


# APPLICATION SCHEMAS


class ApplicationBase(BaseModel):
    student_id: int
    offer_id: int
    status: Status


class ApplicationRead(ApplicationBase):
    ...


class ApplicationCreate(ApplicationBase):
    ...


# SUBJECT SCHEMAS


class Subject(BaseModel):
    student_id: int
    name: str
    grade: int


class SubjectFilter(BaseModel):
    name: str
    grade: int


# STUDENT PROFILE SCHEMAS


class StudentProfileRead(StudentRead):
    experiences: list[ExperienceRead]
    subjects: list[Subject]


class StudentProfileUpdate(StudentUpdate):
    experiences: list[ExperienceUpdate]


class ApplicantRead(StudentBase):
    id: int
    status: str


# STUDENT REPORT SCHEMAS


class StudentReport(BaseModel):
    student_id: int
    offer_id: int
    overall_grade: int
    technical_grade: int
    communication_grade: int
    comment: str
