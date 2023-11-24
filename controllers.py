from models import (StudentCreate, Student, StudentUpdate,
                    CompanyCreate, Company, CompanyUpdate)
from sqlmodel import Session, select
from fastapi import HTTPException, status
from utils import pwd_context
from sqlmodel import SQLModel
from typing import cast


"""
Generic CRUD functions for users. Can be used by all user types
"""

def register_user(user: StudentCreate | CompanyCreate, session: Session, Model) -> Student | Company:
    sql = select(Model).where(Model.email == user.email)
    user_in_db = session.exec(sql).first()
    if user_in_db is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    hashed_password = pwd_context.hash(user.password)
    user_to_insert = Model(
        **user.dict(),
        hashed_password=hashed_password,
    )
    session.add(user_to_insert)
    session.commit()
    session.refresh(user_to_insert)

    return user_to_insert


def get_users(session: Session, Model) -> list[Student] | list[Company]:
    sql = select(Model)
    users = session.exec(sql).all()
    return list(users)


def get_user(user_id: int, session: Session, Model) -> Student | Company:
    user = session.get(Model, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def get_user_by_email(email: str, session: Session, Model) -> Student | Company:
    sql = select(Model).where(Model.email == email)
    user = session.exec(sql).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def update_user(
    user_id: int, 
    fields_to_update: StudentUpdate | CompanyUpdate,
    session: Session,
    current_user: Student | Company,
    Model,
) -> Student | Company:
    if current_user.id != user_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Action not allowed",
        )
    user = cast(Model, get_user(user_id, session, Model))
    updated_fields = fields_to_update.dict(exclude_unset=True)
    for key, value in updated_fields.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(user_id: int, session: Session, current_user: Student | Company, Model) -> Student | Company:
    if current_user.id != user_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Action not allowed",
        )
    user = cast(Model, get_user(user_id, session, Model))
    session.delete(user)
    session.commit()
    return user


""" 
Controllers for STUDENTS. Use the generic functions for user CRUD operations.
"""

def register_student(student: StudentCreate, session: Session) -> Student:
    return cast(Student, register_user(student, session, Student))


def get_students(session: Session) -> list[Student]:
    return cast(list[Student], get_users(session, Student))


def get_student(student_id: int, session: Session) -> Student:
    return cast(Student, get_user(student_id, session, Student))


def get_student_by_email(email: str, session: Session) -> Student:
    return cast(Student, get_user_by_email(email, session, Student))


def update_student(
    student_id: int, 
    fields_to_update: StudentUpdate, 
    session: Session, 
    current_student: Student
) -> Student:
    return cast(Student, update_user(
        student_id, 
        fields_to_update, 
        session, 
        current_student, 
        Student))


def delete_student(student_id: int, session: Session, current_student: Student) -> Student:
    return cast(Student, delete_user(student_id, session, current_student, Student))


""" Controllers for COMPANIES """

def register_company(company: CompanyCreate, session: Session) -> Company:
    return cast(Company, register_user(company, session, Company))


def get_companies(session: Session) -> list[Company]:
    return cast(list[Company], get_users(session, Company))
    

def get_company(company_id: int, session: Session) -> Company:
    return cast(Company, get_user(company_id, session, Company))


def get_company_by_email(email: str, session: Session) -> Company:
    return cast(Company, get_user_by_email(email, session, Company))


def update_company(
    company_id: int, 
    fields_to_update: CompanyUpdate, 
    session: Session, 
    current_user: Company
) -> Company:
    return cast(Company, update_user(
        company_id,
        fields_to_update,
        session,
        current_user,
        Company))


def delete_company(company_id: int, session: Session, current_user: Company) -> Company:
    return cast(Company, delete_user(company_id, session, current_user, Company))