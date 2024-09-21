import pytest
import psycopg as pg
from psycopg.rows import class_row
from .database import get_connection_string
from .enums import Region, Status
from .security import pwd_context
from dataclasses import dataclass
from httpx import AsyncClient


BASE_URL = "http://127.0.0.1:8000"


@dataclass
class CompanyTest:
    id: int
    email: str
    password: str
    hashed_password: str
    name: str
    field: str
    num_employees: int
    year_founded: int
    website: str


@dataclass
class OfferTest:
    id: int
    salary: int
    num_weeks: int
    field: str
    deadline: str
    requirements: str
    responsibilities: str
    company_id: int
    region_id: int


@dataclass
class StudentTest:
    id: int
    email: str
    name: str
    date_of_birth: str
    university: str
    major: str
    credits: int
    gpa: float
    region_id: int
    password: str
    hashed_password: str


@dataclass
class ExperienceTest:
    id: int
    from_date: str
    to_date: str
    company: str
    position: str
    description: str
    student_id: int


@dataclass
class ApplicationTest:
    student_id: int
    offer_id: int
    status: int


def create_offer(company_id: int, offer_id: int = 1, field: str = "Test Field", num_weeks: int = 20) -> OfferTest:
    return OfferTest(
        id=offer_id,
        salary=2000,
        num_weeks=num_weeks,
        field=field,
        deadline="2024-10-01",
        requirements="Test Requirements",
        responsibilities="Test Responsibilities",
        company_id=company_id,
        region_id=Region.GLOBAL.value,
    )


def create_student(student_id: int = 1, email: str = "student@test.com") -> StudentTest:
    return StudentTest(
        id = student_id,
        email = email,
        name = "Test Name",
        date_of_birth = "2000-01-01",
        university = "Test University",
        major = "Test Major",
        credits = 150,
        gpa = 8.50,
        region_id = 0,
        password = "Test Password",
        hashed_password = pwd_context.hash("Test Password"),
    )


def create_company() -> CompanyTest:
    return CompanyTest(
        id=1,
        email="company@test.com",
        password="company-password",
        hashed_password=pwd_context.hash("company-password"),
        name="Test LLC",
        field="Test Field",
        num_employees=230,
        year_founded=1999,
        website="www.test-llc.com",
    )


def create_experience(student_id: int) -> ExperienceTest:
    return ExperienceTest(
        id=1,
        from_date="2021-01-01",
        to_date="2021-12-31",
        company="Test Company Experience",
        position="Test Position",
        description="Test Experience Description",
        student_id=student_id,
    )


def create_application(student_id: int, offer_id: int) -> ApplicationTest:
    return ApplicationTest(
        student_id=student_id,
        offer_id=offer_id,
        status=Status.WAITING.value,
    )


def create_applications(student: StudentTest, offers: list[OfferTest]) -> list[ApplicationTest]:
    applications = []
    for offer in offers:
        application = create_application(student.id, offer.id)
        applications.append(application)
    return applications


async def get_company_token(client: AsyncClient, company: CompanyTest) -> dict:
    response = await client.post(
        url="/token?user_type_param=company",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": company.email,
            "password": company.password,
    })
    token = response.json()
    return token


async def get_company_token_header(client: AsyncClient, company: CompanyTest) -> dict:
    token = await get_company_token(client, company)
    return {"Authorization": f"Bearer {token['access_token']}"}


async def get_student_token(client: AsyncClient, student: StudentTest) -> dict:
    response = await client.post(
        url="/token?user_type_param=student",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": student.email,
            "password": student.password,
    })
    token = response.json()
    return token


async def get_student_token_header(client: AsyncClient, student: StudentTest) -> dict:
    token = await get_student_token(client, student)
    return {"Authorization": f"Bearer {token['access_token']}"}


def create_token_header(token: dict) -> dict:
    return {"Authorization": f"Bearer {token['access_token']}"}


def delete_db_data(db_connection: pg.Connection):
    db_connection.execute("DELETE FROM applications;")
    db_connection.execute("DELETE FROM experiences;")
    db_connection.execute("DELETE FROM offers;")
    db_connection.execute("DELETE FROM students;")
    db_connection.execute("DELETE FROM companies;")
    db_connection.commit()


def get_applications_from_db(offer_id: int) -> list[ApplicationTest]:
    db_string = get_connection_string()
    with pg.connect(db_string) as db_connection:
        cursor = db_connection.cursor(row_factory=class_row(ApplicationTest))
        sql = (
            "SELECT student_id, offer_id, status "
            "FROM applications "
            "WHERE offer_id = %s"
        )
        cursor.execute(sql, params=[offer_id])
        applications = cursor.fetchall()
        cursor.close()
        return applications


@pytest.fixture(scope="module")
def db_connection():
    db_string = get_connection_string()
    with pg.connect(db_string) as db_connection:
        yield db_connection
        delete_db_data(db_connection)


@pytest.fixture(scope="function", autouse=True)
def reset_database(db_connection: pg.Connection):
    delete_db_data(db_connection)


@pytest.fixture(scope="function")
def insert_company_in_db(db_connection: pg.Connection) -> CompanyTest:
    company = create_company()
    db_connection.execute(
        "INSERT INTO companies "
        "(id, email, hashed_password, name, field, num_employees, year_founded, website) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        params=[
            company.id,
            company.email,
            company.hashed_password,
            company.name,
            company.field,
            company.num_employees,
            company.year_founded,
            company.website,
    ])
    db_connection.commit()
    return company


@pytest.fixture(scope="function")
def insert_offers_in_db(db_connection: pg.Connection, insert_company_in_db: CompanyTest) -> dict:
    company = insert_company_in_db
    o1 = create_offer(company.id, offer_id=1, field="Test Field 1", num_weeks=10)
    o2 = create_offer(company.id, offer_id=2, field="Test Field 2", num_weeks=20)
    o3 = create_offer(company.id, offer_id=3, field="Test Field 3", num_weeks=30)
    db_connection.execute(
        "INSERT INTO offers "
        "(id, salary, num_weeks, field, deadline, requirements, responsibilities, company_id, region_id) "
        "VALUES "
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s), "
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s), "
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        params=[
            o1.id, o1.salary, o1.num_weeks, o1.field, o1.deadline, o1.requirements, o1.responsibilities, o1.company_id, o1.region_id,
            o2.id, o2.salary, o2.num_weeks, o2.field, o2.deadline, o2.requirements, o2.responsibilities, o2.company_id, o2.region_id,
            o3.id, o3.salary, o3.num_weeks, o3.field, o3.deadline, o3.requirements, o3.responsibilities, o3.company_id, o3.region_id,
    ])
    db_connection.commit()
    return {"offers": [o1, o2, o3], "company": company}


@pytest.fixture(scope="function")
def insert_student_in_db(db_connection: pg.Connection) -> StudentTest:
    student = create_student()
    db_connection.execute(
        "INSERT INTO students "
        "(id, email, hashed_password, name, university, major, credits, gpa, date_of_birth, region_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
        params=[
            student.id,
            student.email,
            student.hashed_password,
            student.name,
            student.university,
            student.major,
            student.credits,
            student.gpa,
            student.date_of_birth,
            student.region_id,
    ])
    db_connection.commit()
    return student


@pytest.fixture(scope="function")
def insert_experience_in_db(
    insert_student_in_db: StudentTest, 
    db_connection: pg.Connection
) -> dict:
    student = insert_student_in_db
    experience = create_experience(student.id)
    db_connection.execute(
        "INSERT INTO experiences "
        "(id, from_date, to_date, company, position, description, student_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        params=[
            experience.id, 
            experience.from_date, 
            experience.to_date, 
            experience.company, 
            experience.position, 
            experience.description, 
            experience.student_id,
    ])
    db_connection.commit()
    return {
        "student": student,
        "experience": experience,
    }


@pytest.fixture(scope="function")
def insert_student_applications_in_db(
    insert_student_in_db: StudentTest, 
    insert_offers_in_db: dict,
    db_connection: pg.Connection,
) -> dict:
    student = insert_student_in_db
    offers: list[OfferTest] = insert_offers_in_db["offers"]
    applications = create_applications(student, offers)
    
    a1 = applications[0]
    a2 = applications[1]
    a3 = applications[2]

    db_connection.execute(
        "INSERT INTO applications "
        "(student_id, offer_id, status) VALUES "
        "(%s, %s, %s), (%s, %s, %s), (%s, %s, %s)",
        params=[
            a1.student_id, a1.offer_id, a1.status,
            a2.student_id, a2.offer_id, a2.status,
            a3.student_id, a3.offer_id, a3.status,
        ],
    )
    db_connection.commit()
    return {
        "student": student,
        "offers": offers,
        "applications": applications,
    }


@pytest.fixture(scope="function")
def insert_offer_applications_in_db(
    insert_offers_in_db: dict,
    db_connection: pg.Connection,
) -> dict:
    # We want to create multiple applications for the same offer

    offer: OfferTest = insert_offers_in_db["offers"][0]
    company: CompanyTest = insert_offers_in_db["company"]
    
    s1 = create_student(student_id=1, email="student_1@mail.com")
    s2 = create_student(student_id=2, email="student_2@mail.com")
    s3 = create_student(student_id=3, email="student_3@mail.com")
    
    a1 = create_application(s1.id, offer.id)
    a2 = create_application(s2.id, offer.id)
    a3 = create_application(s3.id, offer.id)
    
    insert_students_sql = (
        "INSERT INTO students "
        "(id, email, hashed_password, name, university, major, credits, gpa, date_of_birth, region_id) "
        "VALUES "
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s), "
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s), "
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    )
    insert_applications_sql = (
        "INSERT INTO applications "
        "(student_id, offer_id, status) VALUES "
        "(%s, %s, %s), (%s, %s, %s), (%s, %s, %s);"
    )
    db_connection.execute(insert_students_sql, params=[
        s1.id, s1.email, s1.hashed_password, s1.name, s1.university, s1.major, s1.credits, s1.gpa, s1.date_of_birth, s1.region_id,
        s2.id, s2.email, s2.hashed_password, s2.name, s2.university, s2.major, s2.credits, s2.gpa, s2.date_of_birth, s2.region_id,
        s3.id, s3.email, s3.hashed_password, s3.name, s3.university, s3.major, s3.credits, s3.gpa, s3.date_of_birth, s3.region_id,
    ])
    db_connection.execute(insert_applications_sql, params=[
        a1.student_id, a1.offer_id, a1.status,
        a2.student_id, a2.offer_id, a2.status,
        a3.student_id, a3.offer_id, a3.status,
    ])
    db_connection.commit()

    return {
        "students": [s1, s2, s3],
        "applications": [a1, a2, a3],
        "offer": offer,
        "company": company,
    }