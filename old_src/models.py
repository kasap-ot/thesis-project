from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from pydantic import BaseModel
from fastapi import Query


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
    
    # offers: list["Offer"] = Relationship(back_populates="company")
    

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


""" Models for OFFERS """

class OfferBase(SQLModel):
    salary: int
    num_weeks: int
    field: str
    deadline: date
    requirements: str
    responsibilities: str

    def to_dict(self) -> dict:
        return {
            "salary": self.salary,
            "num_weeks": self.num_weeks,
            "field": self.field,
            "deadline": self.deadline.isoformat(),
            "requirements": self.requirements,
            "responsibilities": self.responsibilities,
        }

    # company_id: int = Field(foreign_key="company.id")


class Offer(OfferBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    
    # company: Company = Relationship(back_populates="offers")


class OfferCreate(OfferBase):
    ...


class OfferRead(OfferBase):
    id: int


class OfferUpdate(SQLModel):
    salary: int | None = None
    num_weeks: int | None = None
    field: str | None = None
    deadline: date | None = None
    requirements: str | None = None
    responsibilities: str | None = None


class OfferFilter(BaseModel):
    min_salary: int | None = Query(default=None, gt=0, alias="min-salary")
    max_salary: int | None = Query(default=None, gt=0, alias="max-salary")
    min_num_weeks: int | None = Query(default=None, gt=0, alias="min-num-weeks")
    max_num_weeks: int | None = Query(default=None, gt=0, alias="max-num-weeks")
    field: str | None = Query(default=None)


"""
class Experience(Base):
    from_date: date
    to_date: date
    company: str
    description: str


class Offer(Base):
    country_id: int
    # min_year: int (not necessary?)


class Application(Base):
    student_id: int
    offer_id: int
    status: Status
"""